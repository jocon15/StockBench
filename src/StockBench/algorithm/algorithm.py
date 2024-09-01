import os
import time
import logging
from typing import ValuesView, Tuple
from StockBench.indicator.trigger import Trigger
from StockBench.constants import BUY_SIDE, SELL_SIDE

log = logging.getLogger()


class Algorithm:
    """
    The Algorithm class encapsulates a strategy dictionary along with other functionality related to using an algorithm.

    The available triggers are selected and stored based on the strategy. This allows the simulator to simply use the
    algorithm as a delegate for checking the rules of the strategy for trigger events.
    True = trigger event hit. False = trigger event not hit.
    """
    FILEPATH_KEY = 'strategy_filepath'

    def __init__(self, strategy: dict, available_indicators: ValuesView):
        self.strategy = strategy
        self.strategy_filename = self.__load_strategy_filename()

        # generic list of available algorithm sorted by side
        self.__buy_only_triggers = []
        self.__sell_only_triggers = []
        self.__side_agnostic_triggers = []
        # sort the indicator algorithm into their respective list
        self.__sort_indicator_trigger_sides(available_indicators)

        self.__basic_error_check_strategy()

    def get_window(self) -> Tuple:
        """Parse the strategy for relevant information needed to make the API request."""
        log.debug('Parsing strategy for timestamps...')

        # __basic_error_check_strategy() guarantees the keys exist
        start_date_unix = int(self.strategy['start'])
        end_date_unix = int(self.strategy['end'])

        self.__error_check_timestamps(start_date_unix, end_date_unix)

        additional_days = self.get_additional_days()

        # add a buffer
        if additional_days != 0:
            # we figure 2 weekdays and a holiday for every week of additional days
            # since it gets cast to int, the decimal is cut off -> it's usually < 3 per week after cast
            additional_days += int((additional_days / 7) * 3)
        # now, we should always have enough days to supply the indicators that the user requires
        return start_date_unix, end_date_unix, additional_days

    def get_additional_days(self) -> int:
        """Calculate number of additional days required for the strategy."""
        # build a list algorithm keys and algorithm values
        keys = []
        values = []
        if 'buy' in self.strategy.keys():
            for key in self.strategy['buy'].keys():
                keys.append(key)
                values.append(self.strategy['buy'][key])
        if 'sell' in self.strategy.keys():
            for key in self.strategy['sell'].keys():
                keys.append(key)
                values.append(self.strategy['sell'][key])

        # assemble all algorithm into a single list
        triggers = [x for n in (self.__side_agnostic_triggers, self.__buy_only_triggers) for x in n]
        triggers = [x for n in (triggers, self.__sell_only_triggers) for x in n]

        # use the algorithm keys/values and algorithm list to calculate the minimum additional days required to run
        # the simulation
        additional_days = 0
        for i in range(len(keys)):
            key = keys[i]
            value = values[i]
            for trigger in triggers:
                if trigger.strategy_symbol in key:
                    num = trigger.additional_days(key, value)
                    if additional_days < num:
                        additional_days = num

        return additional_days

    def add_indicator_data(self, data_manager) -> None:
        """Add indicator data from each algorithm"""
        log.debug('Adding indicators to data based on strategy...')
        # create a list of all algorithm except sell algorithm
        triggers = [x for n in (self.__side_agnostic_triggers, self.__buy_only_triggers) for x in n]

        # find all buy algorithm and add their indicator to the data
        for key in self.strategy['buy'].keys():
            for trigger in triggers:
                if trigger.strategy_symbol in key:
                    trigger.add_to_data(key, self.strategy['buy'][key], 'buy', data_manager)
                elif 'and' in key:
                    for inner_key in self.strategy['buy'][key].keys():
                        if trigger.strategy_symbol in inner_key:
                            trigger.add_to_data(inner_key, self.strategy['buy'][key][inner_key], 'buy', data_manager)

        # create a list of all algorithm except sell algorithm
        triggers = [x for n in (self.__side_agnostic_triggers, self.__sell_only_triggers) for x in n]

        # find all sell algorithm and add their indicator to the data
        for key in self.strategy['sell'].keys():
            for trigger in triggers:
                if trigger.strategy_symbol in key:
                    trigger.add_to_data(key, self.strategy['sell'][key], 'sell', data_manager)
                elif 'and' in key:
                    for inner_key in self.strategy['sell'][key].keys():
                        if trigger.strategy_symbol in inner_key:
                            trigger.add_to_data(inner_key, self.strategy['sell'][key][inner_key], 'sell',
                                                data_manager)

    def check_triggers_by_side(self, side, data_manager, current_day_index, position) -> Tuple[bool, str]:
        """Check all sell triggers for a defined side.

        Args:
            side(str): Buy or sell.
            data_manager (object): The data object.
            current_day_index (int): The index of the current day.
            position (object): The position object.

        return:
            Tuple: boolean was triggered, and the rule string that triggered it

        Notes:
            The key is returned because we need to eventually add it to the position object that gets created
            (or already exists - depending on side) so we can perform rule analytics post-simulation. Even though
            we have a reference to the position object here, we do not record the key that triggered it here because,
            depending on side, the reference may be None. Better to perform the key assignment to position once we have
            a guaranteed position object to add it to.
        """
        was_triggered = False
        triggered_key = ''
        side_keys = self.strategy[side].keys()
        for key in side_keys:
            # handle algorithm
            triggered_key = key
            was_triggered = self.__handle_triggers(data_manager, current_day_index, position, key, side)
            if was_triggered:
                break

        if triggered_key == '':
            raise ValueError(f'Strategy does not have any {side} triggers defined!')

        return was_triggered, self.__get_rule_string(side, triggered_key)

    def __load_strategy_filename(self) -> str:
        # extract filepath if available
        filename = 'unknown'
        if self.FILEPATH_KEY in self.strategy:
            # extract filepath to class attribute
            filename = os.path.basename(self.strategy[self.FILEPATH_KEY])
        return filename

    def __basic_error_check_strategy(self) -> None:
        """Check the strategy for errors"""
        log.debug('Checking strategy for errors...')
        if not self.strategy:
            log.critical('No strategy uploaded')
            raise Exception('No strategy uploaded')
        if 'start' not in self.strategy.keys():
            log.critical("Strategy missing 'start' key")
            raise Exception("Strategy missing 'start' key")
        if 'end' not in self.strategy.keys():
            log.critical("Strategy missing 'end' key")
            raise Exception("Strategy missing 'end' key")
        if BUY_SIDE not in self.strategy.keys():
            log.critical(f"Strategy missing '{BUY_SIDE}' key")
            raise Exception(f"Strategy missing '{BUY_SIDE}' key")
        if SELL_SIDE not in self.strategy.keys():
            log.critical(f"Strategy missing '{SELL_SIDE}' key")
            raise Exception(f"Strategy missing '{SELL_SIDE}' key")
        log.debug('No errors found in the strategy')

    def __sort_indicator_trigger_sides(self, indicators: ValuesView) -> None:
        """Sorts the algorithm of each indicator into their respective list based on trade side.

        Buy - algorithm can be used only to algorithm a position creation.
        Sell - algorithm can only be used to algorithm a position liquidation.
        Agnostic - algorithm can be used for both buying and selling positions.

        Args:
            indicators (list): Generic list of all indicators available in StockBench.
        """
        for indicator in indicators:
            if indicator.get_trigger().get_side() == Trigger.AGNOSTIC:
                self.__side_agnostic_triggers.append(indicator.get_trigger())
            elif indicator.get_trigger().get_side() == Trigger.SELL:
                self.__sell_only_triggers.append(indicator.get_trigger())
            else:
                self.__buy_only_triggers.append(indicator.get_trigger())

    def __handle_triggers(self, data_manager, current_day_index, position, key, side) -> bool:
        """Check all triggers for hits.

        Args:
            data_manager (any): DataManager housing the simulation data.
            current_day_index (int): Index of the current day in the simulation.
            position (any): Currently open position (if applicable).
            key (str): The key of the current context in the strategy.
            side (str): Buy or sell.

        return:
            bool: True if triggered, false if not.
        """
        if side == 'buy':
            # concatenate the agnostic list with the buy list
            triggers = [x for n in (self.__side_agnostic_triggers, self.__buy_only_triggers) for x in n]
        else:
            # concatenate the agnostic list with the sell list
            triggers = [x for n in (self.__side_agnostic_triggers, self.__sell_only_triggers) for x in n]

        if 'and' in key:
            return self.__handle_and_triggers(triggers, data_manager, current_day_index, position, key, side)
        else:
            return self.__handle_or_triggers(triggers, data_manager, current_day_index, position, key, side)

    def __handle_and_triggers(self, triggers, data_manager, current_day_index, position, key, side) -> bool:
        """Check all triggers for hits.

        Args:
            triggers (list): A list of applicable triggers based on side.
            data_manager (any): DataManager housing the simulation data.
            current_day_index (int): Index of the current day in the simulation.
            position (any): Currently open position (if applicable).
            key (str): The key of the current context in the strategy.
            side (str): 'buy' or 'sell'

        return:
            bool: True if triggered, false if not.
        """
        for inner_key in self.strategy[side][key].keys():
            trigger_hit = False
            key_matched_with_trigger = False
            # check all algorithm
            for trigger in triggers:
                if trigger.strategy_symbol in inner_key:
                    key_matched_with_trigger = True
                    trigger_hit = trigger.check_trigger(
                        inner_key,
                        self.strategy[side][key][inner_key],
                        data_manager,
                        position,
                        current_day_index)
            # note: placement of this conditional can be here or inside key check (doesn't matter)
            if not trigger_hit:
                # not all 'AND' triggers were hit
                return False
            if not key_matched_with_trigger:
                raise ValueError(f'Strategy key: {key} did not match any available indicators!')

        # all 'AND' triggers were hit
        return True

    def __handle_or_triggers(self, triggers, data_manager, current_day_index, position, key, side) -> bool:
        """Check all triggers for hits.

        Args:
            triggers (list): A list of applicable triggers based on side.
            data_manager (any): DataManager housing the simulation data.
            current_day_index (int): Index of the current day in the simulation.
            position (any): Currently open position (if applicable).
            key (str): The key of the current context in the strategy.
            side (str): 'buy' or 'sell'

        return:
            bool: True if triggered, false if not.
        """
        key_matched_with_trigger = False
        # check all algorithm
        for trigger in triggers:
            if trigger.strategy_symbol in key:
                key_matched_with_trigger = True
                trigger_hit = trigger.check_trigger(
                    key,
                    self.strategy[side][key],
                    data_manager,
                    position,
                    current_day_index)
                if trigger_hit:
                    # any 'OR' algorithm was hit
                    return True
        if not key_matched_with_trigger:
            raise ValueError(f'Strategy key: {key} did not match any available indicators!')

        # no 'OR' triggers were hit
        return False

    def __get_rule_string(self, side: str, key: str) -> str:
        """Get the rule as a string.

        Args:
            side (str): Buy or sell.
            key (str): The key of strategy rule.

        return:
            The full strategy rule as a string
        """
        return f'{key}:{self.strategy[side][key]}'

    @staticmethod
    def __error_check_timestamps(start_time_unix: int, end_time_unix: int) -> None:
        """Simple check that the timestamps are valid."""
        if start_time_unix > end_time_unix:
            log.critical('Start timestamp must be before end timestamp')
            raise Exception('Start timestamp must be before end timestamp')
        if start_time_unix > int(time.time()):
            log.critical('Start timestamp must not be in the future')
            raise Exception('Start timestamp must not be in the future')