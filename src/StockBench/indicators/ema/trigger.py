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
        # map nums to a list of ints
        nums = list(map(int, re.findall(r'\d+', key)))
        if nums:
            return max(nums)
        # nums is empty
        raise ValueError(f'EMA key: {key} must have a length.')

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
            # add the EMA data to the df
            self.__add_ema(num, data_manager)
        else:
            log.warning(f'Warning: {key} is in incorrect format and will be ignored')
            print(f'Warning: {key} is in incorrect format and will be ignored')

    def check_trigger(self, key, value, data_manager, position_obj, current_day_index) -> bool:
        """Trigger logic for EMA.

        Args:
            key (str): The key value of the trigger.
            value (str): The value of the trigger.
            data_manager (any): The data API object.
            position_obj (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the trigger was hit.
        """
        log.debug(f'Checking EMA trigger: {key}...')

        # get the indicator value from the key
        indicator_value = self.__parse_key(key, data_manager, current_day_index)

        # get the operator and trigger value from the value
        operator, trigger_value = self._parse_value(key, value, data_manager, current_day_index)

        log.debug(f'EMA trigger: {key} checked successfully')

        # trigger checks
        return Trigger.basic_trigger_check(indicator_value, operator, trigger_value)

    def __parse_key(self, key, data_manager, current_day_index) -> float:
        """Parser for parsing the key into the indicator value."""
        # find the indicator value (left hand side of the comparison)
        nums = self.find_all_nums_in_str(key)

        # title of the column in the data
        title = f'EMA{int(nums[0])}'

        if len(nums) == 1:
            indicator_value = float(data_manager.get_data_point(title, current_day_index))
        elif len(nums) == 2:
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
                # re-raise the error so check_trigger() knows the parse failed
                raise ValueError
        else:
            log.warning(f'Warning: {key} is in incorrect format and will be ignored')
            print(f'Warning: {key} is in incorrect format and will be ignored')
            # re-raise the error so check_trigger() knows the parse failed
            raise ValueError

        return indicator_value

    @staticmethod
    def __add_ema(length, data_manager):
        """Pre-calculate the EMA values and add them to the df.

        Args:
            length (int): The length of the EMA to use.
            data_manager (any): The data object.
        """
        # get a list of close price values
        column_title = f'EMA{length}'

        # if we already have EMA values in the df, we don't need to add them again
        for col_name in data_manager.get_column_names():
            if column_title in col_name:
                return

        # get a list of price values as a list
        price_data = data_manager.get_column_data(data_manager.CLOSE)

        # calculate the EMA values
        ema_values = EMATrigger.__calculate_ema(length, price_data)

        # add the calculated values to the df
        data_manager.add_column(column_title, ema_values)

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
