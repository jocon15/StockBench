import re
import logging
import statistics
from StockBench.constants import *
from StockBench.triggers.trigger import Trigger

log = logging.getLogger()


class RSITrigger(Trigger):
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
        if len(nums) > 0:
            for num in nums:
                num = int(num)
                if num > highest_num:
                    highest_num = num
            return highest_num
        else:
            return DEFAULT_RSI_LENGTH

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
            # add the RSI data to the df
            self.__add_rsi(num, data_obj)
        else:
            # add the RSI data to the df
            self.__add_rsi(DEFAULT_RSI_LENGTH, data_obj)
        # ======== value based (rsi limit)=========
        nums = re.findall(r'\d+', value)
        if side == 'buy':
            if len(nums) > 0:
                _trigger = float(nums[0])
                self.__add_lower_rsi(_trigger, data_obj)
        else:
            if len(nums) > 0:
                _trigger = float(nums[0])
                self.__add_upper_rsi(_trigger, data_obj)

    def check_trigger(self, key, value, data_obj, position_obj, current_day_index) -> bool:
        """Trigger logic for RSI.

        Args:
            key (str): The key value of the trigger.
            value (str): The value of the trigger.
            data_obj (any): The data API object.
            position_obj (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the trigger was hit.
        """
        log.debug('Checking RSI triggers...')

        # find nums for potential slope usage
        nums = re.findall(r'\d+', key)

        if len(nums) < 1:
            # get the RSI value for the current day
            rsi = data_obj.get_data_point('RSI', current_day_index)

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
            result = Trigger.basic_triggers_check(rsi, operator, trigger_value)

            log.debug('All stochastic triggers checked')

            return result
        elif len(nums) == 2:
            # likely that the $slope indicator is being used
            if SLOPE_SYMBOL in key:
                title = 'RSI'

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
                result = Trigger.basic_triggers_check(slope, operator, trigger_value)

                log.debug('All RSI triggers checked')

                return result
            else:
                # an exception occurred trying to parse trigger value or operator - skip trigger
                return False

        log.warning(f'Warning: {key} is in incorrect format and will be ignored')
        print(f'Warning: {key} is in incorrect format and will be ignored')
        return False

    @staticmethod
    def __add_rsi(length, data_obj):
        """Pre-calculate the RSI values and add them to the df.

        Args:
            length (int): The length of the RSI to use.
            data_obj (any): The data object.
        """
        # if we already have RSI upper values in the df, we don't need to add them again
        for col_name in data_obj.get_column_names():
            if 'RSI' in col_name:
                return

        # get a list of price values as a list
        price_data = data_obj.get_column_data(data_obj.CLOSE)

        # calculate the RSI values from the indicator API
        rsi_values = RSITrigger.__calculate_rsi(length, price_data)

        # add the calculated values to the df
        data_obj.add_column('RSI', rsi_values)

    @staticmethod
    def __add_upper_rsi(trigger_value, data_obj):
        """Add upper RSI trigger to the df.

        Args:
            trigger_value (float): The trigger value for the upper RSI.
            data_obj (any): The data object.
        """
        # if we already have RSI upper values in the df, we don't need to add them again
        for col_name in data_obj.get_column_names():
            if 'rsi_upper' in col_name:
                return

        # create a list of the trigger value repeated
        list_values = [trigger_value for _ in range(data_obj.get_data_length())]

        # add the list to the data
        data_obj.add_column('RSI_upper', list_values)

    @staticmethod
    def __add_lower_rsi(trigger_value, data_obj):
        """Add lower RSI trigger to the df.

        Args:
            trigger_value (float): The trigger value for the lower RSI.
            data_obj (any): The data object.
        """
        # if we already have RSI lower values in the df, we don't need to add them again
        for col_name in data_obj.get_column_names():
            if 'rsi_upper' in col_name:
                return

        # create a list of the trigger value repeated
        list_values = [trigger_value for _ in range(data_obj.get_data_length())]

        # add the list to the data
        data_obj.add_column('RSI_lower', list_values)

    @staticmethod
    def __calculate_rsi(length: int, price_data: list) -> list:
        """Calculate the RSI values for a list of price values.

        Args:
            length (int): The length of the RSI to calculate.
            price_data (list): The price data to calculate the RSI from.

        return:
            list: The list of calculated RSI values.
        """
        first_day_value = 0
        gain = []
        loss = []
        rsi = []
        all_rsi = []  # archive to return
        for i in range(1, len(price_data)):
            dif = float(price_data[i]) - float(price_data[i - 1])
            if dif > 0:
                if len(gain) == length:
                    gain.pop(0)
                    gain.append(dif)
                else:
                    gain.append(dif)
            elif dif < 0:
                if len(loss) == length:
                    loss.pop(0)
                    loss.append(abs(dif))
                else:
                    loss.append(abs(dif))
            if len(gain) > 0 and len(loss) > 0:
                avg_gain = statistics.mean(gain)
                avg_loss = statistics.mean(loss)
                rs = avg_gain / avg_loss
                rs_index = round(100 - (100 / (1 + rs)), 3)
                if len(rsi) == 6:
                    rsi.pop(0)
                    rsi.append(rs_index)
                else:
                    rsi.append(rs_index)
                if i == 1:
                    first_day_value = rs_index
                all_rsi.append(rs_index)

        # ensure that the data returned is the same size
        # **
        # Note: Given that the simulation has additional days,
        # the days that these values are assigned to will not be seen
        # by the simulation
        # **
        if len(all_rsi) != len(price_data):
            dif = len(price_data) - len(all_rsi)
            for _ in range(dif):
                # append initial values to the front of the list
                all_rsi.insert(0, first_day_value)

        return all_rsi
