import re
import logging
from abc import abstractmethod
from StockBench.constants import *

log = logging.getLogger()


class Trigger:
    """Base class for a trigger. Provides some of the core functionality for a trigger."""
    BUY = 0
    SELL = 1
    AGNOSTIC = 2

    def __init__(self, strategy_symbol, side):
        self.strategy_symbol = strategy_symbol
        self.__side = side

    def get_side(self):
        return self.__side

    @abstractmethod
    def additional_days(self, key, value) -> int:
        raise NotImplementedError('Additional days not implemented!')

    @abstractmethod
    def add_to_data(self, key, value, side, data_manager):
        raise NotImplementedError('Add to data not implemented!')

    @abstractmethod
    def check_trigger(self, key, value, data_manager, position_obj, current_day_index) -> bool:
        raise NotImplementedError('Check trigger not implemented!')

    def _parse_value(self, key, value, data_manager, current_day_index) -> tuple:
        """Parser for parsing the operator and trigger value from the value.

        NOTE: This is the default implementation for this, since it is used frequently in this form.
            For abnormal triggers like candle colors, you can override this with another implementation.
        """
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
                # re-raise the error so check_trigger() knows the parse failed
                raise ValueError

        return operator, trigger_value

    @staticmethod
    def basic_trigger_check(indicator_value, operator_value, trigger_value) -> bool:
        """Abstraction for basic trigger comparison operators.

        Args:
            indicator_value (float): The value of the indicator.
            operator_value (str): The operator defined in the strategy
            trigger_value (float): The value of the trigger.

        returns:
            bool: True if the trigger was hit.
        """
        if operator_value == '<=':
            if indicator_value <= trigger_value:
                return True
        elif operator_value == '>=':
            if indicator_value >= trigger_value:
                return True
        elif operator_value == '<':
            if indicator_value < trigger_value:
                return True
        elif operator_value == '>':
            if indicator_value > trigger_value:
                return True
        elif operator_value == '=':
            if (indicator_value - trigger_value) <= 0.001:  # DOUBLE_COMPARISON_EPSILON
                return True
        return False

    @staticmethod
    def find_single_numeric_in_str(value) -> float:
        """Find a single numeric trigger in a string.

        Args:
            value (str): Any value of the strategy.

        return:
            float: The trigger value in the string.

        raises:
            ValueError: If the passed value is not in the correct format (contains >1 or no numerics).
        """
        nums = re.findall(r'\d+', value)
        if len(nums) == 1:
            return float(nums[0])
        else:
            log.error(f'Invalid amount of numbers found in trigger value: {value}')
            print(f'Invalid amount of numbers found in trigger value: {value}')
            raise ValueError(f'Invalid amount of numbers found in trigger value: {value}')

    @staticmethod
    def find_all_nums_in_str(value) -> list:
        """Finds all number groupings in a string.

        Args:
            value (str): The string to parse.

        return:
            list: A list of numbers in the string.

        """
        return re.findall(r'\d+', value)

    @staticmethod
    def find_operator_in_str(value) -> str:
        """Find the logic operator in a string.

        Args:
            value (str): Any value of the strategy.

        return:
            str: The operator in the string.

        raises:
            ValueError: If the passed value has incorrect amount of number groupings.
        """
        nums = re.findall(r'\d+', value)
        if len(nums) == 1:
            return value.replace(str(nums[0]), '')
        else:
            log.error(f'Invalid number found in trigger value: {value}')
            print(f'Invalid number found in trigger value: {value}')
            # if no trigger value available, exit
            raise ValueError(f'Invalid number found in trigger value: {value}')

    @staticmethod
    def calculate_slope(y2, y1, length) -> float:
        """Calculate the slope between 2 points.

        Args:
            y2(any): The y-value of the final point.
            y1(any): The y-value of the initial point.
            length(any): The difference between the x-values of y2 and y1.

        return:
            float: The slope between the two points.

        raises:
            ValueError: If the length is less than 2.
        """
        if length < 2:
            log.error('Slope window length cannot be less than 2!')
            print('Slope window length cannot be less than 2!')
            raise ValueError('Slope window length cannot be less than 2!')

        # calculate slope
        return round((y2 - y1) / float(length), 2)
