import re
import logging
from StockBench.constants import *
from StockBench.triggers.trigger import Trigger
from StockBench.indicators.indicators import Indicators

log = logging.getLogger()


class RSITrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol)

    def additional_days(self, key) -> int:
        """Calculate the additional days required.

        Args:
            key (any): The key value from the strategy.
        """
        additional_days = 0
        nums = re.findall(r'\d+', key)
        if len(nums) == 1:
            num = int(nums[0])
            if additional_days < num:
                additional_days = num
        else:
            additional_days = DEFAULT_RSI_LENGTH
        return additional_days

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
        if len(nums) == 1:
            num = int(nums[0])
            # add the RSI data to the df
            self.__add_rsi(num, data_obj)
        else:
            # add the RSI data to the df
            self.__add_rsi(DEFAULT_RSI_LENGTH, data_obj)
        # ======== value based (rsi limit)=========
        # _value = self.__strategy['buy'][key]
        _nums = re.findall(r'\d+', value)
        if side == 'buy':
            if len(_nums) == 1:
                _trigger = float(_nums[0])
                self.__add_lower_rsi(_trigger, data_obj)
        else:
            if len(_nums) == 1:
                _trigger = float(_nums[0])
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
        log.debug('Checking stochastic oscillator triggers...')
        # get the RSI value for current day
        # old way where we calculate it on the spot (deprecated)
        # rsi = self.__indicators_API.RSI(_num, current_day_index)
        # new way where we just pull the pre-calculated value from the col in the df
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
                # an exception occurred trying to parse trigger value or operator
                # return false (skip trigger)
                return False

        # trigger checks
        result = Trigger.basic_triggers_check(rsi, operator, trigger_value)

        log.debug('All RSI triggers checked')

        return result

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
        rsi_values = Indicators.RSI(length, price_data)

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
