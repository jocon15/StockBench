"""
This file will hold an SMATrigger subclass that inherits from the trigger class and implements abstract methods.

The sma plugin class will instantiate an instance of this class as an attribute (member variable).

Remember, this architecture allows both the subplot and the trigger functionality to be contained by the plugin
without forcing a complex [multiple] inheritance scheme. The currently used approach can be applied if new
aspects of the plugin are added later on.
"""

import re
import logging
from StockBench.constants import *
from StockBench.triggers.trigger import Trigger

log = logging.getLogger()


class StochasticTrigger(Trigger):
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

    def add_to_data(self, key, value, side, data_obj):
        """Add data to the dataframe.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_obj (any): The data object.
        """
        # ======== key based =========
        nums = re.findall(r'\d+', key)
        if len(nums) > 0:
            num = int(nums[0])
            # add the stochastic data to the df
            self.__add_stochastic_oscillator(num, data_obj)
        else:
            # add the stochastic data to the df
            self.__add_stochastic_oscillator(DEFAULT_STOCHASTIC_OSCILLATOR_LENGTH, data_obj)
        # ======== value based (stochastic limit)=========
        nums = re.findall(r'\d+', value)
        if side == 'buy':
            if len(nums) > 0:
                trigger = float(nums[0])
                self.__add_lower_stochastic(trigger, data_obj)
        else:
            if len(nums) > 0:
                trigger = float(nums[0])
                self.__add_upper_stochastic(trigger, data_obj)

    def check_trigger(self, key, value, data_obj, position_obj, current_day_index) -> bool:
        """Trigger logic for stochastic oscillator.

        Args:
            key (str): The key value of the trigger.
            value (str): The value of the trigger.
            data_obj (any): The data API object.
            position_obj (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the trigger was hit.
        """
        log.debug('Checking stochastic oscillator triggers...')

        # find nums for potential slope usage
        nums = re.findall(r'\d+', key)

        if len(nums) < 2:
            # get the stochastic value for the current day
            stochastic = data_obj.get_data_point('stochastic_oscillator', current_day_index)

            if CURRENT_PRICE_SYMBOL in value:
                trigger_value = float(data_obj.get_data_point(data_obj.CLOSE, current_day_index))
                operator = value.replace(CURRENT_PRICE_SYMBOL, '')
            else:
                # check that the value from {key: value} has a number in it
                try:
                    trigger_value = Trigger.find_numeric_in_str(value)
                    operator = Trigger.find_operator_in_str(value)
                except ValueError:
                    # an exception occurred trying to parse trigger value or operator - skip trigger
                    return False

            # trigger checks
            result = Trigger.basic_triggers_check(stochastic, operator, trigger_value)

            log.debug('All stochastic triggers checked')

            return result
        elif len(nums) == 2:
            # likely that the $slope indicator is being used
            if SLOPE_SYMBOL in key:
                title = 'stochastic_oscillator'

                # get the length of the slope window
                slope_window_length = int(nums[1])
                # data request length is window - 1 to account for the current day index being a part of the window
                slope_data_request_length = slope_window_length - 1

                # get data for slope calculation
                y2 = float(data_obj.get_data_point(title, current_day_index))
                y1 = float(data_obj.get_data_point(title, current_day_index - slope_data_request_length))

                # calculate slope
                slope = round((y2 - y1) / float(slope_window_length), 4)

                # check that the value from {key: value} has a number in it
                try:
                    trigger_value = Trigger.find_numeric_in_str(value)
                    operator = Trigger.find_operator_in_str(value)
                except ValueError:
                    # an exception occurred trying to parse trigger value or operator - skip trigger
                    return False

                # trigger checks
                result = Trigger.basic_triggers_check(slope, operator, trigger_value)

                log.debug('All stochastic triggers checked')

                return result
            else:
                # an exception occurred trying to parse trigger value or operator - skip trigger
                return False

        log.warning(f'Warning: {key} is in incorrect format and will be ignored')
        print(f'Warning: {key} is in incorrect format and will be ignored')
        return False

    @staticmethod
    def __add_stochastic_oscillator(length, data_obj):
        """Pre-calculate the stochastic values and add them to the df.

        Args:
            length (int): The length of the stochastic to use.
            data_obj (any): The data object.
        """
        # if we already have SO values in the df, we don't need to add them again
        for col_name in data_obj.get_column_names():
            if 'stochastic_oscillator' in col_name:
                return

        # get data to calculate SO
        high_data = data_obj.get_column_data(data_obj.HIGH)
        low_data = data_obj.get_column_data(data_obj.LOW)
        close_data = data_obj.get_column_data(data_obj.CLOSE)

        # calculate SO
        stochastic_values = StochasticTrigger.__stochastic_oscillator(length, high_data, low_data, close_data)

        # add the calculated values to the df
        data_obj.add_column('stochastic_oscillator', stochastic_values)

    @staticmethod
    def __add_upper_stochastic(trigger_value, data_obj):
        """Add upper stochastic trigger to the df.

        Args:
            trigger_value (float): The trigger value for the upper stochastic.
            data_obj (any): The data object.
        """
        # if we already have values in the df, we don't need to add them again
        for col_name in data_obj.get_column_names():
            if 'stochastic_upper' in col_name:
                return

        # create a list of the trigger value repeated
        list_values = [trigger_value for _ in range(data_obj.get_data_length())]

        # add the list to the data
        data_obj.add_column('stochastic_upper', list_values)

    @staticmethod
    def __add_lower_stochastic(trigger_value, data_obj):
        """Add lower stochastic trigger to the df.

        Args:
            trigger_value (float): The trigger value for the lower stochastic.
            data_obj (any): The data object.
        """
        # if we already have values in the df, we don't need to add them again
        for col_name in data_obj.get_column_names():
            if 'stochastic_lower' in col_name:
                return

        # create a list of the trigger value repeated
        list_values = [trigger_value for _ in range(data_obj.get_data_length())]

        # add the list to the data
        data_obj.add_column('stochastic_lower', list_values)

    @staticmethod
    def __stochastic_oscillator(length: int, high_data: list, low_data: list, close_data: list) -> list:
        """Calculate the stochastic values for a list of price values.

        Args:
            length (int): The length of the stochastic oscillator to calculate.
            high_data (list): The high price data to calculate the stochastic oscillator from.
            low_data (list): The high price data to calculate the stochastic oscillator from.
            close_data (list): The close price data to calculate the stochastic oscillator from.

        return:
            list: The list of calculated stochastic values.
        """
        past_length_days_high = []
        past_length_days_low = []
        past_length_days_close = []
        stochastic_oscillator = []
        for i in range(len(close_data)):
            if i < length:
                past_length_days_high.append(float(high_data[i]))
                past_length_days_low.append(float(low_data[i]))
                past_length_days_close.append(float(close_data[i]))
            else:
                past_length_days_high.pop(0)
                past_length_days_low.pop(0)
                past_length_days_close.pop(0)
                past_length_days_high.append(float(high_data[i]))
                past_length_days_low.append(float(low_data[i]))
                past_length_days_close.append(float(close_data[i]))

            stochastic_oscillator.append(((float(close_data[i]) - min(past_length_days_low)) /
                                          (max(past_length_days_high) - min(past_length_days_low))) * 100.0)

        return stochastic_oscillator
