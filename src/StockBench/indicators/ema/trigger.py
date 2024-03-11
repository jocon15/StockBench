import re
import logging
import statistics
from StockBench.constants import *
from StockBench.triggers.trigger import Trigger

log = logging.getLogger()


class EMATrigger(Trigger):
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
        nums = re.findall(r'\d+', key)
        if len(nums) > 0:
            # element 0 will be the indicator length
            num = int(nums[0])
            # add the EMA data to the df
            self.__add_ema(num, data_obj)
        else:
            log.warning(f'Warning: {key} is in incorrect format and will be ignored')
            print(f'Warning: {key} is in incorrect format and will be ignored')

    def check_trigger(self, key, value, data_obj, position_obj, current_day_index) -> bool:
        """Trigger logic for EMA.

        Args:
            key (str): The key value of the trigger.
            value (str): The value of the trigger.
            data_obj (any): The data API object.
            position_obj (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the trigger was hit.
        """
        log.debug('Checking EMA triggers...')

        # find the EMA length, else exit
        nums = re.findall(r'\d+', key)
        # since there is no default EMA, there must be a value provided, else exit
        if len(nums) == 1:
            # ensure that num is the correct type
            indicator_length = int(nums[0])

            # column title for the simulation data
            title = f'EMA{indicator_length}'

            # get the ema value for the current day
            ema = float(data_obj.get_data_point(title, current_day_index))

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
            result = Trigger.basic_trigger_check(ema, operator, trigger_value)

            log.debug('All EMA triggers checked')

            return result
        elif len(nums) == 2:
            # likely that the $slope indicator is being used
            if SLOPE_SYMBOL in key:
                # ensure that num is the correct type
                indicator_length = int(nums[0])

                # get the sma value for the current day
                title = f'EMA{indicator_length}'

                # get the length of the slope window
                slope_window_length = int(nums[1])

                if slope_window_length < 2:
                    raise Exception('Slope window lengths cannot be less than 2')

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
                result = Trigger.basic_trigger_check(slope, operator, trigger_value)

                log.debug('All EMA triggers checked')

                return result
            else:
                # an exception occurred trying to parse trigger value or operator - skip trigger
                return False

        log.warning(f'Warning: {key} is in incorrect format and will be ignored')
        print(f'Warning: {key} is in incorrect format and will be ignored')
        return False

    @staticmethod
    def __add_ema(length, data_obj):
        """Pre-calculate the EMA values and add them to the df.

        Args:
            length (int): The length of the EMA to use.
            data_obj (any): The data object.
        """
        # get a list of close price values
        column_title = f'EMA{length}'

        # if we already have EMA values in the df, we don't need to add them again
        for col_name in data_obj.get_column_names():
            if column_title in col_name:
                return

        # get a list of price values as a list
        price_data = data_obj.get_column_data(data_obj.CLOSE)

        # calculate the EMA values
        ema_values = EMATrigger.__calculate_ema(length, price_data)

        # add the calculated values to the df
        data_obj.add_column(column_title, ema_values)

    @staticmethod
    def __calculate_ema(length: int, price_data: list) -> list:
        """Calculates the EMA values for a list of price values.

        Args:
            length (int): The length of the EMA to calculate.
            price_data (list): The price data to calculate the EMA from.

        return:
            list: The list of calculated EMA values.
        """
        # calculate k
        k = 2 / (length + 1)

        # get the initial ema value (uses sma of length days)
        previous_ema = EMATrigger.__calculate_sma(length, price_data[0:length])[-1]

        ema_values = []
        for i in range(len(price_data)):
            if i < length:
                ema_values.append(None)
            else:
                ema = round((k * (float(price_data[i]) - previous_ema)) + previous_ema, 3)
                ema_values.append(ema)
                previous_ema = ema
        return ema_values

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
