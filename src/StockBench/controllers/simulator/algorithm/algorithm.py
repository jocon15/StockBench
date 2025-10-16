import os
import time
import logging
from typing import ValuesView, Tuple, List

from StockBench.controllers.simulator.indicator import Trigger
from StockBench.models.constants.general_constants import BUY_SIDE, SELL_SIDE, START_KEY, END_KEY, AND_KEY
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager
from StockBench.models.position.position import Position
from StockBench.controllers.simulator.algorithm.exceptions import MalformedStrategyError

log = logging.getLogger()


class Algorithm:
    """
    Encapsulates a strategy dictionary along with other functionality related to using an algorithm.

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
        self.__sort_indicator_triggers_by_side(available_indicators)

        self.__validate_strategy()

    def get_simulation_window(self) -> Tuple:
        """Parse the strategy for relevant information needed to make the API request."""
        log.debug('Parsing strategy for timestamps...')

        # __basic_error_check_strategy() guarantees the keys exist
        start_date_unix = int(self.strategy[START_KEY])
        end_date_unix = int(self.strategy[END_KEY])

        self.__validate_timestamps(start_date_unix, end_date_unix)

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
        log.debug('Calculating additional days required data based on strategy...')

        additional_days = 0

        # assemble a list of triggers that could cause a buy
        triggers = [x for n in (self.__side_agnostic_triggers, self.__buy_only_triggers) for x in n]

        # search all buy triggers for additional days
        additional_days = max(additional_days, self.__get_additional_days_per_side(triggers, BUY_SIDE))

        # assemble a list of triggers that could cause a sell
        triggers = [x for n in (self.__side_agnostic_triggers, self.__sell_only_triggers) for x in n]

        # search all sell triggers for additional days
        additional_days = max((additional_days, self.__get_additional_days_per_side(triggers, SELL_SIDE)))

        return additional_days

    def add_indicator_data(self, data_manager) -> None:
        """Add indicator data from each algorithm"""
        log.debug('Adding indicators to data based on strategy...')

        # assemble a list of triggers that could cause a buy
        triggers = [x for n in (self.__side_agnostic_triggers, self.__buy_only_triggers) for x in n]

        # find all buy triggers and add their indicator to the data
        self.__add_to_data_per_side(triggers, BUY_SIDE, data_manager)

        # assemble a list of triggers that could cause a sell
        triggers = [x for n in (self.__side_agnostic_triggers, self.__sell_only_triggers) for x in n]

        # find all sell triggers and add their indicator to the data
        self.__add_to_data_per_side(triggers, SELL_SIDE, data_manager)

    def check_triggers_by_side(self, data_manager: DataManager, current_day_index: int, position: Position,
                               side: str) -> Tuple[bool, str]:
        """Check all triggers for a side.

        Args:
            data_manager: The data object.
            current_day_index: The index of the current day.
            position: The position object.
            side: Buy or sell.

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
            triggered_key = key
            was_triggered = self.__handle_triggers_by_side(data_manager, current_day_index, position, key, side)
            if was_triggered:
                break

        if triggered_key == '':
            raise ValueError(f'Strategy does not have any {side} triggers defined!')

        return was_triggered, self.__get_rule_string(triggered_key, side)

    def __load_strategy_filename(self) -> str:
        """Load the filename from the strategy if it is available."""
        filename = 'unknown'
        try:
            if self.FILEPATH_KEY in self.strategy:
                # extract filepath to class attribute
                filename = os.path.basename(self.strategy[self.FILEPATH_KEY])
        except TypeError:
            raise MalformedStrategyError('Filepath is not defined in strategy!')
        return filename

    def __validate_strategy(self) -> None:
        """Check the strategy for errors."""
        log.debug('Checking strategy for errors...')
        if not self.strategy:
            log.critical('No strategy uploaded')
            raise Exception('No strategy uploaded')
        if START_KEY not in self.strategy.keys():
            log.critical("Strategy missing START_KEY key")
            raise Exception("Strategy missing START_KEY key")
        if END_KEY not in self.strategy.keys():
            log.critical("Strategy missing END_KEY key")
            raise Exception("Strategy missing END_KEY key")
        if BUY_SIDE not in self.strategy.keys():
            log.critical(f"Strategy missing '{BUY_SIDE}' key")
            raise Exception(f"Strategy missing '{BUY_SIDE}' key")
        if SELL_SIDE not in self.strategy.keys():
            log.critical(f"Strategy missing '{SELL_SIDE}' key")
            raise Exception(f"Strategy missing '{SELL_SIDE}' key")
        log.debug('No errors found in the strategy')

    def __sort_indicator_triggers_by_side(self, indicators: ValuesView) -> None:
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

    def __get_additional_days_per_side(self, triggers: list, side: str) -> int:
        """Finds the number of additional days required per side."""
        additional_days = 0
        for rule_key in self.strategy[side].keys():
            rule_value = self.strategy[side][rule_key]
            for trigger in triggers:
                if AND_KEY in rule_key:
                    for inner_key in rule_value.keys():
                        inner_value = rule_value[inner_key]
                        if trigger.indicator_symbol in inner_key:
                            additional_days = max(additional_days, trigger.calculate_additional_days_from_rule_key(inner_key,
                                                                                                                   inner_value))
                        elif trigger.indicator_symbol in inner_value:
                            additional_days = max(additional_days, trigger.calculate_additional_days_from_rule_value(inner_value))
                elif trigger.indicator_symbol in rule_key:
                    additional_days = max(additional_days, trigger.calculate_additional_days_from_rule_key(rule_key, rule_value))
                elif trigger.indicator_symbol in rule_value:
                    additional_days = max(additional_days, trigger.calculate_additional_days_from_rule_value(rule_value))
        return additional_days

    def __add_to_data_per_side(self, triggers: list, side: str, data_manager: DataManager):
        """Adds the indicator data to the data manager per side."""
        for rule_key in self.strategy[side].keys():
            rule_value = self.strategy[side][rule_key]
            for trigger in triggers:
                if AND_KEY in rule_key:
                    for inner_key in rule_value.keys():
                        inner_value = rule_value[inner_key]
                        if trigger.indicator_symbol in inner_key:
                            trigger.add_indicator_data_from_rule_key(inner_key, inner_value, side, data_manager)
                        elif trigger.indicator_symbol in inner_value:
                            trigger.add_indicator_data_from_rule_value(inner_value, side, data_manager)
                elif trigger.indicator_symbol in rule_key:
                    trigger.add_indicator_data_from_rule_key(rule_key, rule_value, side, data_manager)
                elif trigger.indicator_symbol in rule_value:
                    trigger.add_indicator_data_from_rule_value(rule_value, side, data_manager)

    def __handle_triggers_by_side(self, data_manager: DataManager, current_day_index: int, position: Position, key: str,
                                  side: str) -> bool:
        """Check all triggers of a side for hits.

        Args:
            data_manager: DataManager housing the simulation data.
            current_day_index: Index of the current day in the simulation.
            position: Currently open position (if applicable).
            key: The key of the current context in the strategy.
            side: Buy or sell.

        return:
            bool: True if triggered, false if not.
        """
        if side == BUY_SIDE:
            # assemble triggers that could cause a buy
            triggers = [x for n in (self.__side_agnostic_triggers, self.__buy_only_triggers) for x in n]
        else:
            # assemble triggers that could trigger a sell
            triggers = [x for n in (self.__side_agnostic_triggers, self.__sell_only_triggers) for x in n]

        if AND_KEY in key:
            return self.__handle_and_triggers(triggers, data_manager, current_day_index, position, key, side)
        else:
            return self.__handle_or_triggers(triggers, data_manager, current_day_index, position, key, side)

    def __handle_and_triggers(self, triggers: List[Trigger], data_manager: DataManager, current_day_index: int,
                              position: Position, key: str, side: str) -> bool:
        """Check all triggers for hits.

        Args:
            triggers: A list of applicable triggers based on side.
            data_manager: DataManager housing the simulation data.
            current_day_index: Index of the current day in the simulation.
            position: Currently open position (if applicable).
            key: The key of the current context in the strategy.
            side: BUY_SIDE or SELL_SIDE

        return:
            bool: True if triggered, false if not.
        """
        for inner_key in self.strategy[side][key].keys():
            inner_value = self.strategy[side][key][inner_key]
            trigger_hit = False
            key_matched_with_trigger = False
            for trigger in triggers:
                if trigger.indicator_symbol in inner_key:
                    key_matched_with_trigger = True
                    # replace any rule values with indicator references with their actual value
                    injected_inner_value = self._inject_rule_value_with_values(inner_value, triggers, data_manager,
                                                                               current_day_index)
                    trigger_hit = trigger.check_trigger(inner_key, injected_inner_value, data_manager, position,
                                                        current_day_index)
            # placement of this conditional can be here or inside key check (doesn't matter)
            if not trigger_hit:
                # not all AND_KEY triggers were hit
                return False
            if not key_matched_with_trigger:
                raise ValueError(f'Strategy key: {key} did not match any available indicators!')

        # all AND_KEY triggers were hit
        return True

    def __handle_or_triggers(self, triggers: List[Trigger], data_manager: DataManager, current_day_index: int,
                             position: Position, key: str, side: str) -> bool:
        """Check all triggers for hits.

        Args:
            triggers: A list of applicable triggers based on side.
            data_manager: DataManager housing the simulation data.
            current_day_index: Index of the current day in the simulation.
            position: Currently open position (if applicable).
            key: The key of the current context in the strategy.
            side: BUY_SIDE or SELL_SIDE

        return:
            bool: True if triggered, false if not.
        """
        rule_value = self.strategy[side][key]
        key_matched_with_trigger = False
        for trigger in triggers:
            if trigger.indicator_symbol in key:
                key_matched_with_trigger = True
                # replace any rule values that have indicator references with their actual value
                injected_rule_value = self._inject_rule_value_with_values(rule_value, triggers, data_manager,
                                                                          current_day_index)
                trigger_hit = trigger.check_trigger(key, injected_rule_value, data_manager, position, current_day_index)
                if trigger_hit:
                    # any 'OR' trigger was hit
                    return True
        if not key_matched_with_trigger:
            raise ValueError(f'Strategy key: {key} did not match any available indicators!')

        # no 'OR' triggers were hit
        return False

    def __get_rule_string(self, key: str, side: str) -> str:
        """Get the rule as a string.

        Args:
            key: The key of strategy rule.
            side: Buy or sell.

        return:
            The full strategy rule as a string
        """
        return f'{key}:{self.strategy[side][key]}'

    @staticmethod
    def _inject_rule_value_with_values(rule_value: any, triggers: list, data_manager: DataManager,
                                       current_day_index: int) -> str:
        """Replaces indicators in rule value with indicator values."""
        for trigger in triggers:
            if trigger.indicator_symbol in rule_value:
                # pull out comparison operator (comparison operator always comes before indicator symbol in rule value)
                injected_rule_value = rule_value.split(trigger.indicator_symbol)[0]
                # inject the indicator value into the right side of the comparison
                injected_rule_value += str(trigger.get_indicator_value_when_referenced(rule_value, data_manager,
                                                                                       current_day_index))
                return injected_rule_value

        # not all rules will require an injection which is ok, just return the rule_value
        return rule_value

    @staticmethod
    def __validate_timestamps(start_time_unix: int, end_time_unix: int) -> None:
        """Simple check that the timestamps are valid.

        Args:
            start_time_unix: The unix start timestamp.
            end_time_unix: The unix end timestamp.

        raises:
            ValueError: If start timestamp is not chronologically before end timestamp.
            ValueError: If the start timestamp is not chronologically before the current time.
            ValueError: If the end timestamp is not chronologically before the current time.
        """
        if start_time_unix > end_time_unix:
            log.critical('Start timestamp must be before end timestamp')
            raise ValueError('Start timestamp must be before end timestamp')

        current_time = int(time.time())
        if start_time_unix > current_time:
            log.critical('Start timestamp must not be in the future')
            raise ValueError('Start timestamp must not be in the future')

        if end_time_unix > current_time:
            log.critical('End timestamp must not be in the future')
            raise ValueError('End timestamp must not be in the future')
