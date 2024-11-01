import logging
from StockBench.constants import *
from StockBench.indicator.trigger import Trigger
from StockBench.indicator.exceptions import StrategyIndicatorError

log = logging.getLogger()


class PriceTrigger(Trigger):
    # cannot use strategy symbol because its "price"
    DISPLAY_NAME = 'Price'

    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol, side=Trigger.AGNOSTIC)

    def additional_days(self, key, value) -> int:
        """Calculate the additional days required.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from the strategy.
        """
        # note price does not require any additional days
        return 0

    def add_to_data(self, key, value, side, data_manager):
        """Add data to the dataframe.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (any): The data object.
        """
        # note price (OHLC) is in the data by default
        # no need to add it
        return

    def check_trigger(self, key, value, data_manager, position, current_day_index) -> bool:
        """Trigger logic for price.

        Args:
            key (str): The key value of the algorithm.
            value (str): The value of the algorithm.
            data_manager (any): The data API object.
            position (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the algorithm was hit.
        """
        log.debug(f'Checking price algorithm: {key}...')

        # get the indicator value from the key
        indicator_value = self.__parse_key(key, data_manager, current_day_index)

        # get the operator and algorithm value from the value
        operator, trigger_value = self._parse_value(value, data_manager, current_day_index)

        log.debug(f'Price algorithm: {key} checked successfully')

        # algorithm checks
        return Trigger.basic_trigger_check(indicator_value, operator, trigger_value)

    def __parse_key(self, key, data_manager, current_day_index) -> float:
        """Parser for parsing the key into the indicator value."""
        # find the indicator value (left hand side of the comparison)
        nums = self.find_all_nums_in_str(key)

        # title of the column in the data
        title = data_manager.CLOSE

        if len(nums) == 0:
            if SLOPE_SYMBOL in key:
                raise StrategyIndicatorError(f'{self.DISPLAY_NAME} key: {key} does not contain enough number '
                                             f'groupings!')
            indicator_value = float(data_manager.get_data_point(title, current_day_index))
        elif len(nums) == 1:
            # likely that the $slope indicator is being used
            if SLOPE_SYMBOL in key:
                # get the length of the slope window
                slope_window_length = int(nums[0])

                # data request length is window - 1 to account for the current day index being a part of the window
                slope_data_request_length = slope_window_length - 1

                # calculate slope
                indicator_value = self.calculate_slope(
                    float(data_manager.get_data_point(title, current_day_index)),
                    float(data_manager.get_data_point(title, current_day_index - slope_data_request_length)),
                    slope_window_length
                )
            else:
                raise StrategyIndicatorError(f'{self.DISPLAY_NAME} key: {key} contains too many number groupings! '
                                             f'Are you missing a $slope emblem?')
        else:
            raise StrategyIndicatorError(f'{self.DISPLAY_NAME} key: {key} contains too many number groupings!')

        return indicator_value
