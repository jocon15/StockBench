import logging
from StockBench.triggers.volume_trigger import VolumeTrigger
from StockBench.triggers.stop_profit_trigger import StopProfitTrigger
from StockBench.triggers.stop_loss_trigger import StopLossTrigger
from StockBench.triggers.stochastic_trigger import StochasticTrigger
from StockBench.triggers.sma_trigger import SMATrigger
from StockBench.triggers.rsi_trigger import RSITrigger
from StockBench.triggers.price_trigger import PriceTrigger
from StockBench.triggers.candlestick_color_trigger import CandlestickColorTrigger

log = logging.getLogger()


class TriggerManager:
    """This class defines a TriggerAPI object.

    The TriggerAPI object is designed to be used as an API for the simulator to abstract the triggering methods for
    each rule. To keep it simple for the simulator, there are 2 defined entry points, check buy and check sell
    triggers. The rest of the complex triggering logic gets implemented here.

    The goal of the 2 API functions is to return a boolean. True = trigger hit. False = trigger not hit. Both of these
    return values hold for buy or sell.
    """
    def __init__(self, strategy):
        # strategy does not get cleared
        self.__strategy = strategy
        # All below attributes get cleared after trigger call
        self.__data_object = None
        self.__position_object = None
        self.__current_day_index = None
        # Add new triggers to check here
        self.__triggers = (
            StochasticTrigger('stochastic'),
            RSITrigger('RSI'),
            SMATrigger('SMA'),
            VolumeTrigger('volume'),
            CandlestickColorTrigger('color'),
            PriceTrigger('price'),
            StopLossTrigger('stop_loss'),
            StopProfitTrigger('stop_profit')
        )

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

    def __clear_attributes(self):
        self.__data_object = None
        self.__position_object = None
        self.__current_day_index = None

    def __handle_triggers(self, _key, side):
        if _key == 'and':
            # ===== AND Triggers =====

            for inner_key in self.__strategy[side][_key].keys():
                # reset trigger indicator
                trigger_hit = False

                # check all triggers
                for trigger in self.__triggers:
                    if trigger.strategy_symbol in inner_key:
                        trigger_hit = trigger.check_trigger(
                            inner_key,
                            self.__strategy[side][_key][inner_key],
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
            for trigger in self.__triggers:
                if trigger.strategy_symbol in _key:
                    trigger_hit = trigger.check_trigger(
                        _key,
                        self.__strategy[side][_key],
                        self.__data_object,
                        self.__position_object,
                        self.__current_day_index)

            if trigger_hit:
                # any 'OR' trigger was hit
                return True

            # no 'OR' triggers were hit
            return False
