"""
This file will hold an SMATrigger subclass that inherits from the trigger class and implements abstract methods.

The sma indicator class will instantiate an instance of this class as an attribute (member variable).

Remember, this architecture allows both the subplot and the trigger functionality to be contained by the indicator
without forcing a complex [multiple] inheritance scheme. The currently used approach can be applied if new
aspects of the indicator are added later on.
"""

import re
import logging
import statistics
from StockBench.constants import *
from StockBench.triggers.trigger import Trigger

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
        highest_num = 0
        nums = re.findall(r'\d+', key)
        for num in nums:
            num = int(num)
            if num > highest_num:
                highest_num = num
        return highest_num

    def add_to_data(self, key, value, side, data_manager):
        """Add data to the dataframe.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (any): The data object.
        """
        nums = re.findall(r'\d+', key)
        if len(nums) > 0:
            # element 0 will be the indicator length
            num = int(nums[0])
            # add the SMA data to the df
            self.__add_sma(num, data_manager)
        else:
            log.warning(f'Warning: {key} is in incorrect format and will be ignored')
            print(f'Warning: {key} is in incorrect format and will be ignored')

    def check_trigger(self, key, value, data_manager, position_obj, current_day_index) -> bool:
        """Trigger logic for SMA.

        Args:
            key (str): The key value of the trigger.
            value (str): The value of the trigger.
            data_manager (any): The data API object.
            position_obj (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the trigger was hit.
        """
        log.debug('Checking SMA triggers...')

        # find the operator and trigger value (right hand side of the comparison)
        if CURRENT_PRICE_SYMBOL in value:
            trigger_value = float(data_manager.get_data_point(data_manager.CLOSE, current_day_index))
            operator = value.replace(CURRENT_PRICE_SYMBOL, '')
        else:
            # check that the value from {key: value} has a number in it
            try:
                trigger_value = self.find_single_numeric_in_str(value)
                operator = self.find_operator_in_str(value)
            except ValueError:
                log.warning(f'Warning: {key} is in incorrect format and will be ignored')
                print(f'Warning: {key} is in incorrect format and will be ignored')
                return False

        # find the indicator value (left hand side of the comparison)
        nums = self.find_all_nums_in_str(key)
        # since there is no default SMA, there must be a value provided, else exit
        if len(nums) == 1:
            # ensure that num is the correct type
            indicator_length = int(nums[0])

            # get the sma value for the current day
            title = f'SMA{indicator_length}'

            indicator_value = float(data_manager.get_data_point(title, current_day_index))
        elif len(nums) == 2:
            # likely that the $slope indicator is being used
            if SLOPE_SYMBOL in key:
                # get the sma value for the current day
                title = f'SMA{int(nums[0])}'

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
                log.warning(f'Warning: {key} is in incorrect format and will be ignored')
                print(f'Warning: {key} is in incorrect format and will be ignored')
                return False
        else:
            log.warning(f'Warning: {key} is in incorrect format and will be ignored')
            print(f'Warning: {key} is in incorrect format and will be ignored')
            return False

        log.debug('All SMA triggers checked')

        # trigger checks
        return Trigger.basic_trigger_check(indicator_value, operator, trigger_value)

    @staticmethod
    def __add_sma(length, data_manager):
        """Pre-calculate the SMA values and add them to the df.

        Args:
            length (int): The length of the SMA to use.
            data_manager (any): The data object.
        """
        # get a list of close price values
        column_title = f'SMA{length}'

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
