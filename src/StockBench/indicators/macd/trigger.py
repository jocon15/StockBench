import logging
import statistics
from StockBench.constants import *
from StockBench.indicator.trigger import Trigger

log = logging.getLogger()


class MACDTrigger(Trigger):

    LARGE_EMA_LENGTH = 26

    SMALL_EMA_LENGTH = 12

    DATA_COLUMN_TITLE = 'MACD'

    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol, side=Trigger.AGNOSTIC)

    def additional_days(self, key, value) -> int:
        """Calculate the additional days required.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from the strategy.
        """
        return self.LARGE_EMA_LENGTH

    def add_to_data(self, key, value, side, data_manager):
        """Add data to the dataframe.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (any): The data object.
        """
        # if we already have MACD values in the df, we don't need to add them again
        for col_name in data_manager.get_column_names():
            if self.DATA_COLUMN_TITLE == col_name:
                return

        # get a list of price values as a list
        price_data = data_manager.get_column_data(data_manager.CLOSE)

        # add the calculated values to the df
        data_manager.add_column(self.DATA_COLUMN_TITLE, self.__calculate_macd(price_data))

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
        log.debug(f'Checking MACD trigger: {key}...')

        # get the indicator value from the key
        indicator_value = self.__parse_key(key, data_manager, current_day_index)

        # get the operator and trigger value from the value
        operator, trigger_value = self._parse_value(key, value, data_manager, current_day_index)

        log.debug(f'MACD trigger: {key} checked successfully')

        # trigger checks
        return Trigger.basic_trigger_check(indicator_value, operator, trigger_value)

    def __parse_key(self, key, data_manager, current_day_index) -> float:
        """Parser for parsing the key into the indicator value.

        Args:
            key (any): The key value from the strategy.
            data_manager (any): The data object.
            current_day_index (int): The index of the current day.

        return:
            float: The indicator value found in the key.
        """

        # find the indicator value (left hand side of the comparison)
        nums = self.find_all_nums_in_str(key)

        # MACD can only have slope emblem therefore 1 or 0 number groupings are acceptable
        if len(nums) == 0:
            if SLOPE_SYMBOL in key:
                log.critical(f"MACD key: {key} does not contain enough number groupings!")
                print(f"MACD key: {key} does not contain enough number groupings!")
                raise ValueError(f"MACD key: {key} does not contain enough number groupings!")
            indicator_value = float(data_manager.get_data_point(self.DATA_COLUMN_TITLE, current_day_index))
        elif len(nums) == 1:
            # likely that the $slope indicator is being used
            if SLOPE_SYMBOL in key:
                # get the length of the slope window
                slope_window_length = int(nums[0])

                # data request length is window - 1 to account for the current day index being a part of the window
                slope_data_request_length = slope_window_length - 1

                # calculate slope
                indicator_value = self.calculate_slope(
                    float(data_manager.get_data_point(self.DATA_COLUMN_TITLE, current_day_index)),
                    float(data_manager.get_data_point(self.DATA_COLUMN_TITLE, current_day_index -
                                                      slope_data_request_length)),
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

    def __calculate_macd(self, price_data: list) -> list:
        """Calculate MACD values for a list of price values.

        Args:
            price_data (list): The price data to calculate the MACD from.

        return:
            list: The list of calculated MACD values.
        """
        large_ema_length_values = MACDTrigger.__calculate_ema(self.LARGE_EMA_LENGTH, price_data)

        small_ema_length_values = MACDTrigger.__calculate_ema(self.SMALL_EMA_LENGTH, price_data)

        if len(large_ema_length_values) != len(small_ema_length_values):
            raise ArithmeticError('EMA value lists for MACD must be the same length!')

        macd_values = []
        for i in range(len(large_ema_length_values)):
            if large_ema_length_values[i] is None or small_ema_length_values[i] is None:
                # some early values of ema are None until sufficient data is available,
                # just set the MACD to None in these situations
                macd_values.append(None)
            else:
                # calculate the actual MACD
                macd_values.append(round(small_ema_length_values[i] - large_ema_length_values[i], 3))

        return macd_values

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
        previous_ema = MACDTrigger.__calculate_sma(length, price_data[0:length])[-1]

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
