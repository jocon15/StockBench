import re
import logging
from StockBench.constants import *
from StockBench.triggers.trigger import Trigger

log = logging.getLogger()


class PriceTrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol, side=Trigger.AGNOSTIC)

    def additional_days(self, key, value) -> int:
        """Calculate the additional days required.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from the strategy.
        """
        # note price does not require any additional days
        return 0

    def add_to_data(self, key, value, side, data_obj):
        """Add data to the dataframe.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_obj (any): The data object.
        """
        # note price (OHLC) is in the data by default
        # no need to add it
        return

    def check_trigger(self, key, value, data_obj, position_obj, current_day_index) -> bool:
        """Trigger logic for price.

        Args:
            key (str): The key value of the trigger.
            value (str): The value of the trigger.
            data_obj (any): The data API object.
            position_obj (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the trigger was hit.
        """
        log.debug('Checking price triggers...')

        title = data_obj.CLOSE

        if SLOPE_SYMBOL in key:

            # find nums for potential slope usage
            nums = re.findall(r'\d+', key)

            # ensure that the nums list only has 1 number 'price$slope2' where the number is the slope length
            if len(nums) != 1:
                raise Exception('Price key with slope keyword is not in correct format!')

            # get the length of the slope window
            slope_window_length = int(nums[0])

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
        else:
            # get the price data point
            price = data_obj.get_data_point(title, current_day_index)

            # check that the value from {key: value} has a number in it
            try:
                trigger_value = Trigger.find_numeric_in_str(value)
                operator = Trigger.find_operator_in_str(value)
            except ValueError:
                # an exception occurred trying to parse trigger value or operator - skip trigger
                return False

            # trigger checks
            result = Trigger.basic_trigger_check(price, operator, trigger_value)

        log.debug('All Price triggers checked')

        # catch all case if nothing was hit (which is ok!)
        return result
