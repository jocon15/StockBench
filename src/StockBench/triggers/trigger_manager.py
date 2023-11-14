import logging
from StockBench.triggers.trigger import Trigger

log = logging.getLogger()


class TriggerManager:
    """This class defines a TriggerAPI object.

    The TriggerAPI object is designed to be used as an API for the simulator to abstract the triggering methods for
    each rule. To keep it simple for the simulator, there are 2 defined entry points, check buy and check sell
    triggers. The rest of the complex triggering logic gets implemented here.

    The goal of the 2 API functions is to return a boolean. True = trigger hit. False = trigger not hit. Both of these
    return values hold for buy or sell.
    """
    def __init__(self, strategy, plugins: list):
        # strategy does not get cleared
        self.__strategy = strategy
        # All below attributes get cleared after trigger call
        self.__data_object = None
        self.__position_object = None
        self.__current_day_index = None
        # ===== Add new triggers to check here =====
        # triggers that can result in a buy or sell

        self.__plugins = plugins

        self.__side_agnostic_triggers = []
        self.__buy_only_triggers = []
        self.__sell_only_triggers = []
        # sort the plugin triggers into their respective list
        self.__sort_plugin_sides()

    def calculate_strategy_timestamps(self) -> int:
        """"""
        additional_days = 0

        # build a list of sub keys from the buy and sell sections
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

        # assemble a list of all triggers
        triggers = [x for n in (self.__side_agnostic_triggers, self.__buy_only_triggers) for x in n]
        triggers = [x for n in (triggers, self.__sell_only_triggers) for x in n]

        for i in range(len(keys)):
            key = keys[i]
            value = values[i]
            for trigger in triggers:
                if trigger.strategy_symbol in key:
                    num = trigger.additional_days(key, value)
                    if additional_days < num:
                        additional_days = num

        return additional_days

    def parse_strategy_rules(self, data_obj):
        """"""
        # create a list of all triggers except sell triggers
        triggers = [x for n in (self.__side_agnostic_triggers, self.__buy_only_triggers) for x in n]

        # buy keys
        for key in self.__strategy['buy'].keys():
            for trigger in triggers:
                if trigger.strategy_symbol in key:
                    trigger.add_to_data(key, self.__strategy['buy'][key], 'buy', data_obj)
                elif 'and' in key:
                    for inner_key in self.__strategy['buy'][key].keys():
                        if trigger.strategy_symbol in inner_key:
                            trigger.add_to_data(inner_key, self.__strategy['buy'][key][inner_key], 'buy', data_obj)

        # create a list of all triggers except sell triggers
        triggers = [x for n in (self.__side_agnostic_triggers, self.__sell_only_triggers) for x in n]

        # sell keys
        for key in self.__strategy['sell'].keys():
            for trigger in triggers:
                if trigger.strategy_symbol in key:
                    trigger.add_to_data(key, self.__strategy['sell'][key], 'sell', data_obj)
                elif 'and' in key:
                    for inner_key in self.__strategy['sell'][key].keys():
                        if trigger.strategy_symbol in inner_key:
                            trigger.add_to_data(inner_key, self.__strategy['sell'][key][inner_key], 'sell', data_obj)

    def check_buy_triggers(self, data_obj, current_day_index) -> bool:
        """Check all buy triggers.

        Args:
            data_obj (object): The data object.
            current_day_index (int): The index of the current day.

        returns:
            bool: True if triggered, False otherwise.
        """
        self.__data_object = data_obj
        self.__current_day_index = current_day_index

        was_triggered = False
        buy_keys = self.__strategy['buy'].keys()
        for key in buy_keys:
            print(key)
            # handle triggers
            was_triggered = self.__handle_triggers(key, side='buy')
            if was_triggered:
                break

        self.__clear_attributes()
        return was_triggered

    def check_sell_triggers(self, data_obj, position_obj, current_day_index) -> bool:
        """Check all buy triggers.

        Args:
            data_obj (object): The data object.
            position_obj (object): The position object.
            current_day_index (int): The index of the current day.

        returns:
            bool: True if triggered, False otherwise.
        """
        self.__data_object = data_obj
        self.__position_object = position_obj
        self.__current_day_index = current_day_index

        was_triggered = False
        sell_keys = self.__strategy['sell'].keys()
        for key in sell_keys:
            # handle and triggers
            was_triggered = self.__handle_triggers(key, side='sell')
            if was_triggered:
                break
        self.__clear_attributes()
        return was_triggered

    def __sort_plugin_sides(self):
        for plugin in self.__plugins:
            if plugin.get_trigger().get_side() == Trigger.AGNOSTIC:
                self.__side_agnostic_triggers.append(plugin.get_trigger())
            elif plugin.get_trigger().get_side() == Trigger.SELL:
                self.__sell_only_triggers.append(plugin.get_trigger())
            else:
                self.__buy_only_triggers.append(plugin.get_trigger())

    def __clear_attributes(self):
        self.__data_object = None
        self.__position_object = None
        self.__current_day_index = None

    def __handle_triggers(self, key, side):
        """Handle all triggers.

        Args:
            key (str): The key of the current context in the strategy.
            side (str): 'buy' or 'sell'
        """
        if side == 'buy':
            # concatenate the 2 lists
            triggers = [x for n in (self.__side_agnostic_triggers, self.__buy_only_triggers) for x in n]
        else:
            # concatenate the 2 lists
            triggers = [x for n in (self.__side_agnostic_triggers, self.__sell_only_triggers) for x in n]

        if 'and' in key:
            # ===== AND Triggers =====

            for inner_key in self.__strategy[side][key].keys():
                # reset trigger indicator
                trigger_hit = False

                # check all triggers
                for trigger in triggers:
                    if trigger.strategy_symbol in inner_key:
                        trigger_hit = trigger.check_trigger(
                            inner_key,
                            self.__strategy[side][key][inner_key],
                            self.__data_object,
                            self.__position_object,
                            self.__current_day_index)
                if not trigger_hit:
                    # not all 'AND' triggers were hit
                    return False

            # all 'AND' triggers were hit
            return True
        else:
            # ===== OR Triggers =====

            # the triggers are buy
            trigger_hit = False

            # check all triggers
            for trigger in triggers:
                if trigger.strategy_symbol in key:
                    trigger_hit = trigger.check_trigger(
                        key,
                        self.__strategy[side][key],
                        self.__data_object,
                        self.__position_object,
                        self.__current_day_index)
                    if trigger_hit:
                        # any 'OR' trigger was hit
                        return True

            # no 'OR' triggers were hit
            return False
