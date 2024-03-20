import logging
from StockBench.indicator.trigger import Trigger

log = logging.getLogger()


class TriggerManager:
    """
    The TriggerAPI object is designed to be used as an API for the simulator to abstract the triggering methods for
    each rule. To keep it simple for the simulator, there are 2 defined entry points, check buy and check sell
    trigger. The rest of the complex triggering logic gets implemented here.

    The goal of the 2 API functions is to return a boolean. True = trigger hit. False = trigger not hit. Both of these
    return values hold for buy or sell.
    """
    def __init__(self, strategy, indicators):
        self.__strategy = strategy

        # generic list of available trigger sorted by side
        self.__buy_only_triggers = []
        self.__sell_only_triggers = []
        self.__side_agnostic_triggers = []
        # sort the indicator trigger into their respective list
        self.__sort_indicator_trigger_sides(indicators)

    def get_additional_days(self) -> int:
        """Calculate number of additional days required for the strategy."""
        # build a list trigger keys and trigger values
        keys = []
        values = []
        if 'buy' in self.__strategy.keys():
            for key in self.__strategy['buy'].keys():
                keys.append(key)
                values.append(self.__strategy['buy'][key])
        if 'sell' in self.__strategy.keys():
            for key in self.__strategy['sell'].keys():
                keys.append(key)
                values.append(self.__strategy['sell'][key])

        # assemble all trigger into a single list
        triggers = [x for n in (self.__side_agnostic_triggers, self.__buy_only_triggers) for x in n]
        triggers = [x for n in (triggers, self.__sell_only_triggers) for x in n]

        # use the trigger keys/values and trigger list to calculate the minimum additional days required to run
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

    def add_indicator_data(self, data_manager):
        """Add indicator data from each trigger"""
        log.debug('Adding indicators to data based on strategy...')
        # create a list of all trigger except sell trigger
        triggers = [x for n in (self.__side_agnostic_triggers, self.__buy_only_triggers) for x in n]

        # find all buy trigger and add their indicator to the data
        for key in self.__strategy['buy'].keys():
            for trigger in triggers:
                if trigger.strategy_symbol in key:
                    trigger.add_to_data(key, self.__strategy['buy'][key], 'buy', data_manager)
                elif 'and' in key:
                    for inner_key in self.__strategy['buy'][key].keys():
                        if trigger.strategy_symbol in inner_key:
                            trigger.add_to_data(inner_key, self.__strategy['buy'][key][inner_key], 'buy', data_manager)

        # create a list of all trigger except sell trigger
        triggers = [x for n in (self.__side_agnostic_triggers, self.__sell_only_triggers) for x in n]

        # find all sell trigger and add their indicator to the data
        for key in self.__strategy['sell'].keys():
            for trigger in triggers:
                if trigger.strategy_symbol in key:
                    trigger.add_to_data(key, self.__strategy['sell'][key], 'sell', data_manager)
                elif 'and' in key:
                    for inner_key in self.__strategy['sell'][key].keys():
                        if trigger.strategy_symbol in inner_key:
                            trigger.add_to_data(inner_key, self.__strategy['sell'][key][inner_key], 'sell',
                                                data_manager)

    def check_buy_triggers(self, data_manager, current_day_index) -> bool:
        """Check all buy trigger.

        Args:
            data_manager (object): The data object.
            current_day_index (int): The index of the current day.

        returns:
            bool: True if triggered, False otherwise.
        """
        was_triggered = False
        buy_keys = self.__strategy['buy'].keys()
        for key in buy_keys:
            # handle trigger
            was_triggered = self.__handle_triggers(data_manager, current_day_index, None, key, side='buy')
            if was_triggered:
                break

        return was_triggered

    def check_sell_triggers(self, data_manager, position, current_day_index) -> bool:
        """Check all sell trigger.

        Args:
            data_manager (object): The data object.
            position (object): The position object.
            current_day_index (int): The index of the current day.

        returns:
            bool: True if triggered, False otherwise.
        """
        was_triggered = False
        sell_keys = self.__strategy['sell'].keys()
        for key in sell_keys:
            # handle and trigger
            was_triggered = self.__handle_triggers(data_manager, current_day_index, position, key, side='sell')
            if was_triggered:
                break
        return was_triggered

    def __sort_indicator_trigger_sides(self, indicators: list):
        """Sorts the trigger of each indicator into their respective list based on trade side.

        Buy - trigger can be used only to trigger a position creation.
        Sell - trigger can only be used to trigger a position liquidation.
        Agnostic - trigger can be used for both buying and selling positions.

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

    def __handle_triggers(self, data_manager, current_day_index, position, key, side):
        """Check all triggers for hits.

        Args:
            data_manager (any): DataManager housing the simulation data.
            current_day_index (int): Index of the current day in the simulation.
            position (any): Currently open position (if applicable).
            key (str): The key of the current context in the strategy.
            side (str): 'buy' or 'sell'
        """
        if side == 'buy':
            # concatenate the agnostic list with the buy list
            triggers = [x for n in (self.__side_agnostic_triggers, self.__buy_only_triggers) for x in n]
        else:
            # concatenate the agnostic list with the sell list
            triggers = [x for n in (self.__side_agnostic_triggers, self.__sell_only_triggers) for x in n]

        if 'and' in key:
            # ===== AND Triggers =====
            for inner_key in self.__strategy[side][key].keys():
                trigger_hit = False
                key_matched_with_trigger = False
                # check all trigger
                for trigger in triggers:
                    if trigger.strategy_symbol in inner_key:
                        key_matched_with_trigger = True
                        trigger_hit = trigger.check_trigger(
                            inner_key,
                            self.__strategy[side][key][inner_key],
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
        else:
            # ===== OR Triggers =====
            key_matched_with_trigger = False
            # check all trigger
            for trigger in triggers:
                if trigger.strategy_symbol in key:
                    key_matched_with_trigger = True
                    trigger_hit = trigger.check_trigger(
                        key,
                        self.__strategy[side][key],
                        data_manager,
                        position,
                        current_day_index)
                    if trigger_hit:
                        # any 'OR' trigger was hit
                        return True
            if not key_matched_with_trigger:
                raise ValueError(f'Strategy key: {key} did not match any available indicators!')

            # no 'OR' triggers were hit
            return False
