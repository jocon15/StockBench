import logging
from StockBench.constants import *
from StockBench.indicator.trigger import Trigger

log = logging.getLogger()


class VolumeTrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol, side=Trigger.AGNOSTIC)

    def additional_days(self, key, value) -> int:
        """Calculate the additional days required.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from the strategy.
        """
        # volume does not require additional days
        return 0

    def add_to_data(self, key, value, side, data_manager):
        """Add data to the dataframe.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (any): The data object.
        """
        # candle colors are added by default so just return
        return

    def check_trigger(self, key, value, data_manager, position, current_day_index) -> bool:
        """Trigger logic for volume.

        Args:
            key (str): The key value of the algorithm.
            value (str): The value of the algorithm.
            data_manager (any): The data API object.
            position (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the algorithm was hit.
        """
        volume = data_manager.get_data_point(data_manager.VOLUME, current_day_index)

        if CURRENT_PRICE_SYMBOL in value:
            trigger_value = float(data_manager.get_data_point(data_manager.CLOSE, current_day_index))
            operator = value.replace(CURRENT_PRICE_SYMBOL, '')
        else:
            # check that the value from {key: value} has a number in it
            try:
                trigger_value = Trigger.find_single_numeric_in_str(value)
                operator = Trigger.find_operator_in_str(value)
            except ValueError:
                # an exception occurred trying to parse algorithm value or operator - skip algorithm
                return False

        # algorithm checks
        result = Trigger.basic_trigger_check(volume, operator, trigger_value)

        log.debug('All volume algorithm checked')

        return result
