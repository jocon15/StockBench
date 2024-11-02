import logging
import statistics
from StockBench.constants import *
from StockBench.indicator.trigger import Trigger
from StockBench.indicator.exceptions import StrategyIndicatorError

log = logging.getLogger()


class SMATrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol, side=Trigger.AGNOSTIC)

    def additional_days(self, key, value) -> int:
        """Calculate the additional days required.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from the strategy.
        """
        # map nums to a list of ints
        nums = list(map(int, self.find_all_nums_in_str(key)))
        if nums:
            return max(nums)
        # nums is empty
        raise StrategyIndicatorError(f'{self.strategy_symbol} key: {key} must have an indicator length!')

    def add_to_data(self, key, value, side, data_manager):
        """Add data to the dataframe.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (any): The data object.
        """
        nums = self.find_all_nums_in_str(key)
        if len(nums) > 0:
            # element 0 will be the indicator length
            indicator_length = int(nums[0])
            # add the EMA data to the df
            self.__add_sma(indicator_length, data_manager)
        else:
            raise StrategyIndicatorError(f'{self.strategy_symbol} key: {key} must have an indicator length!')

    def check_trigger(self, key, value, data_manager, position, current_day_index) -> bool:
        """Trigger logic for SMA.

        Args:
            key (str): The key value of the algorithm.
            value (str): The value of the algorithm.
            data_manager (any): The data API object.
            position (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the algorithm was hit.
        """
        log.debug(f'Checking {self.strategy_symbol} algorithm: {key}...')

        # get the indicator value from the key
        indicator_value = self.__parse_key(key, data_manager, current_day_index)

        # get the operator and algorithm value from the value
        operator, trigger_value = self._parse_value(value, data_manager, current_day_index)

        log.debug(f'{self.strategy_symbol} algorithm: {key} checked successfully')

        # algorithm checks
        return Trigger.basic_trigger_check(indicator_value, operator, trigger_value)

    def __parse_key(self, key, data_manager, current_day_index) -> float:
        """Parser for parsing the key into the indicator value."""
        # find the indicator value (left hand side of the comparison)
        nums = self.find_all_nums_in_str(key)

        # do not build title outside of conditional as nums could be [] which would result in index error

        if len(nums) == 1:
            if SLOPE_SYMBOL in key:
                raise StrategyIndicatorError(f'{self.strategy_symbol} key: {key} does not contain enough number '
                                             f'groupings!')
            # title of the column in the data
            title = f'{self.strategy_symbol}{int(nums[0])}'
            indicator_value = float(data_manager.get_data_point(title, current_day_index))
        elif len(nums) == 2:
            # title of the column in the data
            title = f'{self.strategy_symbol}{int(nums[0])}'
            # likely that the $slope indicator is being used
            if SLOPE_SYMBOL in key:
                # get the length of the slope window
                slope_window_length = int(nums[1])

                # data request length is window - 1 to account for the current day index being a part of the window
                slope_data_request_length = slope_window_length - 1

                # calculate slope
                indicator_value = self.calculate_slope(
                    float(data_manager.get_data_point(title, current_day_index)),
                    float(data_manager.get_data_point(title, current_day_index - slope_data_request_length)),
                    slope_window_length
                )
            else:
                raise StrategyIndicatorError(f'{self.strategy_symbol} key: {key} contains too many number groupings! '
                                             f'Are you missing a $slope emblem?')
        else:
            raise StrategyIndicatorError(f'{self.strategy_symbol} key: {key} contains too many number groupings!')

        return indicator_value

    def __add_sma(self, length, data_manager):
        """Pre-calculate the SMA values and add them to the df.

        Args:
            length (int): The length of the SMA to use.
            data_manager (any): The data object.
        """
        # get a list of close price values
        column_title = f'{self.strategy_symbol}{length}'

        # if SMA values ar already in the df, we don't need to add them again
        for col_name in data_manager.get_column_names():
            if column_title in col_name:
                return

        # get a list of price values as a list
        price_data = data_manager.get_column_data(data_manager.CLOSE)

        # calculate the SMA values from the indicator API
        sma_values = SMATrigger.__calculate_sma(length, price_data)

        # add the calculated values to the df
        data_manager.add_column(column_title, sma_values)

    @staticmethod
    def __calculate_sma(length: int, price_data: list) -> list:
        """Calculates the SMA values for a list of price values.

        Args:
            length (int): The length of the SMA to calculate.
            price_data (list): The price data to calculate the SMA from.

        return:
            list: The list of calculated SMA values.

        Notes:
            This requires you to keep track of all SMA values so that all values can be added to the df.
        """
        price_values = []
        sma_values = []
        all_sma_values = []
        for element in price_data:
            if len(price_values) < length:
                price_values.append(float(element))
            else:
                price_values.pop(0)
                sma_values.pop(0)
                price_values.append(float(element))
            avg = round(statistics.mean(price_values), 3)
            sma_values.append(avg)
            all_sma_values.append(avg)
        return all_sma_values
