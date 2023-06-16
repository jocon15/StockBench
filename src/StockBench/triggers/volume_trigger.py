import logging
from StockBench.constants import *
from StockBench.triggers.trigger import Trigger

log = logging.getLogger()


class VolumeTrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol)

    def additional_days(self, key, data_obj) -> int:
        """Calculate the additional days required.

        Args:
            key (any): The key value from the strategy.
            data_obj (any): The data object.
        """
        # note volume does not require additional days
        return 0

    def add_to_data(self, key, value, side, data_obj):
        """Add data to the dataframe.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_obj (any): The data object.
        """
        # note that volume is a default parameter and thus already
        # included in the OHLC data so no need to add it
        return

    def check_trigger(self, key, value, data_obj, position_obj, current_day_index) -> bool:
        """Trigger logic for volume.

        Args:
            key (str): The key value of the trigger.
            value (str): The value of the trigger.
            data_obj (any): The data API object.
            position_obj (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the trigger was hit.
        """
        volume = data_obj.get_data_point(data_obj.VOLUME, current_day_index)

        if CURRENT_PRICE_SYMBOL in value:
            trigger_value = float(data_obj.get_data_point(data_obj.CLOSE, current_day_index))
            operator = value.replace(CURRENT_PRICE_SYMBOL, '')
        else:
            # check that the value from {key: value} has a number in it
            try:
                trigger_value = Trigger.find_numeric_in_str(value)
                operator = Trigger.find_operator_in_str(value)
            except ValueError:
                # an exception occurred trying to parse trigger value or operator
                # return false (skip trigger)
                return False

        # trigger checks
        result = Trigger.basic_triggers_check(volume, operator, trigger_value)

        log.debug('All volume triggers checked')

        return result
