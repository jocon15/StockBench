import logging
import statistics
from StockBench.constants import *
from StockBench.indicator.trigger import Trigger
from StockBench.indicator.exceptions import StrategyIndicatorError
from StockBench.simulation_data.data_manager import DataManager

log = logging.getLogger()


class EMATrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol, side=Trigger.AGNOSTIC)

    def additional_days(self, rule_key, value_value) -> int:
        """Calculate the additional days required.

        Args:
            rule_key (any): The key value from the strategy.
            value_value (any): The value from the strategy.
        """
        # map nums to a list of ints
        nums = list(map(int, self.find_all_nums_in_str(rule_key)))
        if nums:
            return max(nums)
        raise StrategyIndicatorError(f'{self.strategy_symbol} key: {rule_key} must have an indicator length!')

    def add_to_data(self, rule_key, rule_value, side, data_manager):
        """Add data to the dataframe.

        Args:
            rule_key (any): The key value from the strategy.
            rule_value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (DataManager): The data object.
        """
        nums = self.find_all_nums_in_str(rule_key)
        if len(nums) > 0:
            indicator_length = int(nums[0])
            self.__add_ema(indicator_length, data_manager)
        else:
            raise StrategyIndicatorError(f'{self.strategy_symbol} key: {rule_key} must have an indicator length!')

    def check_trigger(self, rule_key, rule_value, data_manager, position, current_day_index) -> bool:
        """Trigger logic for EMA.

        Args:
            rule_key (any): The key value of the algorithm.
            rule_value (any): The value of the algorithm.
            data_manager (DataManager): The data API object.
            position (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the algorithm was hit.
        """
        log.debug(f'Checking {self.strategy_symbol} algorithm: {rule_key}...')

        indicator_value = self.__parse_key(rule_key, data_manager, current_day_index)

        operator, trigger_value = self._parse_rule_value(rule_value, data_manager, current_day_index)

        log.debug(f'{self.strategy_symbol} algorithm: {rule_key} checked successfully')

        return Trigger.basic_trigger_check(indicator_value, operator, trigger_value)

    def __parse_key(self, rule_key: str, data_manager: DataManager, current_day_index: int) -> float:
        """Parser for parsing the key into the indicator value."""
        key_number_groupings = self.find_all_nums_in_str(rule_key)

        if len(key_number_groupings) == 1:
            if SLOPE_SYMBOL in rule_key:
                raise StrategyIndicatorError(f'{self.strategy_symbol} rule key: {rule_key} does not contain '
                                             f'enough number groupings!')
            column_title = f'{self.strategy_symbol}{int(key_number_groupings[0])}'
            indicator_value = float(data_manager.get_data_point(column_title, current_day_index))
        elif len(key_number_groupings) == 2:
            column_title = f'{self.strategy_symbol}{int(key_number_groupings[0])}'
            # 2 number groupings suggests the $slope indicator is being used
            if SLOPE_SYMBOL in rule_key:
                slope_window_length = int(key_number_groupings[1])

                # data request length is window - 1 to account for the current day index being a part of the window
                slope_data_request_length = slope_window_length - 1

                indicator_value = self.calculate_slope(
                    float(data_manager.get_data_point(column_title, current_day_index)),
                    float(data_manager.get_data_point(column_title, current_day_index - slope_data_request_length)),
                    slope_window_length
                )
            else:
                raise StrategyIndicatorError(f'{self.strategy_symbol} rule key: {rule_key} contains too many number '
                                             f'groupings! Are you missing a $slope emblem?')
        else:
            raise StrategyIndicatorError(f'{self.strategy_symbol} rule key: {rule_key} contains invalid number '
                                         f'groupings!')

        return indicator_value

    def __add_ema(self, length: int, data_manager: DataManager):
        """Pre-calculate the EMA values and add them to the df."""
        column_title = f'{self.strategy_symbol}{length}'

        # if we already have EMA values in the df, we don't need to add them again
        for col_name in data_manager.get_column_names():
            if column_title in col_name:
                return

        price_data = data_manager.get_column_data(data_manager.CLOSE)

        ema_values = EMATrigger.__calculate_ema(length, price_data)

        data_manager.add_column(column_title, ema_values)

    @staticmethod
    def __calculate_ema(length: int, price_data: list) -> list:
        """Calculates the EMA values for a list of price values"""
        k = 2 / (length + 1)

        # get the initial ema value (uses sma of length days)
        previous_ema = EMATrigger.__calculate_sma(length, price_data[0:length])[-1]

        ema_values = []
        for i in range(len(price_data)):
            if i < length:
                ema_values.append(None)
            else:
                ema_point = round((k * (float(price_data[i]) - previous_ema)) + previous_ema, 3)
                ema_values.append(ema_point)
                previous_ema = ema_point
        return ema_values

    @staticmethod
    def __calculate_sma(length: int, price_data: list) -> list:
        """Calculates the SMA values for a list of price values."""
        price_values = []
        sma_values = []
        for day in price_data:
            if len(price_values) < length:
                price_values.append(float(day))
            else:
                price_values.pop(0)
                sma_values.pop(0)
                price_values.append(float(day))
            avg = round(statistics.mean(price_values), 3)
            sma_values.append(avg)
        return sma_values
