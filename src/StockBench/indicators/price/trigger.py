import logging
from StockBench.constants import *
from StockBench.indicator.trigger import Trigger
from StockBench.indicator.exceptions import StrategyIndicatorError

log = logging.getLogger()


class PriceTrigger(Trigger):
    # cannot use strategy symbol because its "price"
    DISPLAY_NAME = 'Price'

    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=Trigger.AGNOSTIC)

    def additional_days_from_rule_key(self, rule_key, rule_value) -> int:
        """Calculate the additional days required from rule key.

        Args:
            rule_key (any): The key value from the strategy.
            rule_value (any): The key value from the strategy (unused in this function).
        """
        # price does not require any additional days
        return 0

    def additional_days_from_rule_value(self, rule_value: any) -> int:
        """Calculate the additional days required from rule value."""
        # price does not require any additional days
        return 0

    def add_to_data_from_rule_key(self, rule_key, rule_value, side, data_manager):
        """Add data to the dataframe.

        Args:
            rule_key (any): The key value from the strategy.
            rule_value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (any): The data object.
        """
        # note price (OHLC) is in the data by default, no need to add it
        return

    def check_trigger(self, rule_key, rule_value, data_manager, position, current_day_index) -> bool:
        """Trigger logic for price.

        Args:
            rule_key (str): The key value of the algorithm.
            rule_value (str): The value of the algorithm.
            data_manager (any): The data API object.
            position (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if a trigger was hit.
        """
        log.debug(f'Checking price algorithm: {rule_key}...')

        # price uses special key parses because the indicator called 'price', but in the data it is 'close', to make it
        # more clear we are using a dedicate parser
        indicator_value = self.__parse_key(rule_key, data_manager, current_day_index)

        log.debug(f'Price algorithm: {rule_key} checked successfully')

        return self.basic_trigger_check(indicator_value, rule_value, data_manager, current_day_index)

    def __parse_key(self, rule_key, data_manager, current_day_index) -> float:
        """Parser for parsing the key into the indicator value."""
        key_number_groupings = self.find_all_nums_in_str(rule_key)

        if len(key_number_groupings) == 0:
            if SLOPE_SYMBOL in rule_key:
                raise StrategyIndicatorError(f'{self.DISPLAY_NAME} rule key: {rule_key} does not contain enough number '
                                             f'groupings!')
            indicator_value = float(data_manager.get_data_point(data_manager.CLOSE, current_day_index))
        elif len(key_number_groupings) == 1:
            # 1 number group suggests the $slope indicator is being used
            if SLOPE_SYMBOL in rule_key:
                slope_window_length = int(key_number_groupings[0])

                # data request length is window - 1 to account for the current day index being a part of the window
                slope_data_request_length = slope_window_length - 1

                indicator_value = self.calculate_slope(
                    float(data_manager.get_data_point(data_manager.CLOSE, current_day_index)),
                    float(data_manager.get_data_point(data_manager.CLOSE, current_day_index -
                                                      slope_data_request_length)), slope_window_length)
            else:
                raise StrategyIndicatorError(f'{self.DISPLAY_NAME} rule key: {rule_key} contains too many number '
                                             f'groupings! Are you missing a $slope emblem?')
        else:
            raise StrategyIndicatorError(f'{self.DISPLAY_NAME} rule key: {rule_key} contains invalid number groupings!')

        return indicator_value
