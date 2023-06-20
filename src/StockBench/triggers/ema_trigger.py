import re
import logging
from StockBench.constants import *
from StockBench.triggers.trigger import Trigger
from StockBench.indicators.indicators import Indicators

log = logging.getLogger()


class EMATrigger(Trigger):
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
        return additional_days

    def add_to_data(self, key, side, value, data_obj):
        """Add data to the dataframe.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_obj (any): The data object.
        """
        nums = re.findall(r'\d+', key)
        if len(nums) == 1:
            num = int(nums[0])
            # add the EMA data to the df
            self.__add_ema(num, data_obj)

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
        _nums = re.findall(r'\d+', key)
        # since we have no default EMA, there must be a value provided, else exit
        if len(_nums) == 1:
            _num = int(_nums[0])

            # get the ema value for the current day
            title = f'EMA{_num}'
            ema = data_obj.get_data_point(title, current_day_index)

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
            result = Trigger.basic_triggers_check(ema, operator, trigger_value)

            log.debug('All EMA triggers checked')

            return result

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

        # calculate the EMA values from the indicator API
        ema_values = Indicators.EMA(length, price_data)

        # add the calculated values to the df
        data_obj.add_column(column_title, ema_values)