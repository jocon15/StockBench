"""
This file will hold an SMATrigger subclass that inherits from the trigger class and implements abstract methods.

The sma indicator class will instantiate an instance of this class as an attribute (member variable).

Remember, this architecture allows both the subplot and the trigger functionality to be contained by the indicator
without forcing a complex [multiple] inheritance scheme. The currently used approach can be applied if new
aspects of the indicator are added later on.
"""

import logging
from StockBench.constants import *
from StockBench.indicator.trigger import Trigger

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
        # map nums to a list of ints
        nums = list(map(int, self.find_all_nums_in_str(key)))
        if nums:
            return max(nums)
        # nums is empty
        return DEFAULT_STOCHASTIC_OSCILLATOR_LENGTH

    def add_to_data(self, key, value, side, data_manager):
        """Add data to the dataframe.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (any): The data object.
        """
        # ======== key based =========
        nums = self.find_all_nums_in_str(key)
        if len(nums) > 0:
            num = int(nums[0])
            # add the stochastic data to the df
            self.__add_stochastic_oscillator(num, data_manager)
        else:
            # add the stochastic data to the df
            self.__add_stochastic_oscillator(DEFAULT_STOCHASTIC_OSCILLATOR_LENGTH, data_manager)
        # ======== value based (stochastic limit)=========
        nums = self.find_all_nums_in_str(value)
        if side == 'buy':
            if len(nums) > 0:
                trigger = float(nums[0])
                self.__add_lower_stochastic(trigger, data_manager)
        else:
            if len(nums) > 0:
                trigger = float(nums[0])
                self.__add_upper_stochastic(trigger, data_manager)

    def check_trigger(self, key, value, data_manager, position_obj, current_day_index) -> bool:
        """Trigger logic for stochastic oscillator.

        Args:
            key (str): The key value of the trigger.
            value (str): The value of the trigger.
            data_manager (any): The data API object.
            position_obj (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the trigger was hit.
        """
        log.debug(f'Checking stochastic oscillator trigger: {key}...')

        # get the indicator value from the key
        indicator_value = self.__parse_key(key, data_manager, current_day_index)

        # get the operator and trigger value from the value
        operator, trigger_value = self._parse_value(key, value, data_manager, current_day_index)

        log.debug(f'Stochastic oscillator trigger: {key} checked successfully')

        # trigger checks
        return Trigger.basic_trigger_check(indicator_value, operator, trigger_value)

    def __parse_key(self, key, data_manager, current_day_index) -> float:
        """Parser for parsing the key into the indicator value."""
        # find the indicator value (left hand side of the comparison)
        nums = self.find_all_nums_in_str(key)

        if len(nums) == 0:
            # stochastic is default length (14)
            if SLOPE_SYMBOL in key:
                log.critical(f"stochastic key: {key} contains too many number groupings!")
                print(f"stochastic key: {key} contains too many number groupings!")
                raise ValueError(f"stochastic key: {key} contains too many number groupings!")
            # title of the column in the data
            title = 'stochastic_oscillator'
            indicator_value = float(data_manager.get_data_point(title, current_day_index))
        elif len(nums) == 1:
            if SLOPE_SYMBOL in key:
                # make sure the number is after the slope emblem and not the stochastic emblem
                if key.split(str(nums))[0] == 'stochastic' + SLOPE_SYMBOL:
                    log.critical(f"stochastic key: {key} contains no slope value!")
                    print(f"stochastic key: {key} contains no slope value!")
                    raise ValueError(f"stochastic key: {key} contains no slope value!")
            # stochastic is custom length (not 14)
            # title of the column in the data
            title = 'stochastic_oscillator'
            indicator_value = float(data_manager.get_data_point(title, current_day_index))
        elif len(nums) == 2:
            # title of the column in the data
            title = f'stochastic_oscillator{int(nums[0])}'
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
                log.warning(f'Warning: {key} is in incorrect format and will be ignored')
                print(f'Warning: {key} is in incorrect format and will be ignored')
                raise ValueError(f"stochastic key: {key} contains too many number groupings!")
        else:
            log.warning(f'Warning: {key} is in incorrect format and will be ignored')
            print(f'Warning: {key} is in incorrect format and will be ignored')
            raise ValueError(f"stochastic key: {key} contains too many number groupings!")

        return indicator_value

    @staticmethod
    def __add_stochastic_oscillator(length, data_manager):
        """Pre-calculate the stochastic values and add them to the df.

        Args:
            length (int): The length of the stochastic to use.
            data_manager (any): The data object.
        """
        # if we already have SO values in the df, we don't need to add them again
        for col_name in data_manager.get_column_names():
            if 'stochastic_oscillator' in col_name:
                return

        # get data to calculate the indicator value
        high_data = data_manager.get_column_data(data_manager.HIGH)
        low_data = data_manager.get_column_data(data_manager.LOW)
        close_data = data_manager.get_column_data(data_manager.CLOSE)

        # calculate SO
        stochastic_values = StochasticTrigger.__stochastic_oscillator(length, high_data, low_data, close_data)

        # add the calculated values to the df
        data_manager.add_column('stochastic_oscillator', stochastic_values)

    @staticmethod
    def __add_upper_stochastic(trigger_value, data_manager):
        """Add upper stochastic trigger to the df.

        Args:
            trigger_value (float): The trigger value for the upper stochastic.
            data_manager (any): The data object.
        """
        # if we already have values in the df, we don't need to add them again
        for col_name in data_manager.get_column_names():
            if 'stochastic_upper' in col_name:
                return

        # create a list of the trigger value repeated
        list_values = [trigger_value for _ in range(data_manager.get_data_length())]

        # add the list to the data
        data_manager.add_column('stochastic_upper', list_values)

    @staticmethod
    def __add_lower_stochastic(trigger_value, data_manager):
        """Add lower stochastic trigger to the df.

        Args:
            trigger_value (float): The trigger value for the lower stochastic.
            data_manager (any): The data object.
        """
        # if we already have values in the df, we don't need to add them again
        for col_name in data_manager.get_column_names():
            if 'stochastic_lower' in col_name:
                return

        # create a list of the trigger value repeated
        list_values = [trigger_value for _ in range(data_manager.get_data_length())]

        # add the list to the data
        data_manager.add_column('stochastic_lower', list_values)

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

            stochastic_oscillator.append(round(((float(close_data[i]) - min(past_length_days_low)) /
                                                (max(past_length_days_high) - min(past_length_days_low))) * 100.0, 3))

        return stochastic_oscillator
