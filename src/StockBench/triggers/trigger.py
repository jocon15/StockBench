import re
import logging
from abc import abstractmethod

log = logging.getLogger()


class Trigger:
    BUY = 1
    SELL = 2
    AGNOSTIC = 3

    def __init__(self, strategy_symbol, side):
        self.strategy_symbol = strategy_symbol
        self.__side = side

    def get_side(self):
        return self.__side

    @abstractmethod
    def additional_days(self, key, value) -> int:
        raise NotImplementedError('Additional days not implemented!')

    @abstractmethod
    def add_to_data(self, key, value, side, data_obj):
        raise NotImplementedError('Add to data not implemented!')

    @abstractmethod
    def check_trigger(self, key, value, data_obj, position_obj, current_day_index) -> bool:
        raise NotImplementedError('Check trigger not implemented!')

    @staticmethod
    def basic_triggers_check(indicator_value, operator_value, trigger_value) -> bool:
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
            if (indicator_value - trigger_value) <= 0.001:  # DOUBLE_COMPARISON_EPSILON:
                return True
        return False

    @staticmethod
    def find_numeric_in_str(value) -> float:
        """Find the numeric trigger in a string.

        Args:
            value (str): Any value of the strategy.

        return:
            float: The trigger value in the string.

        raises:
            ValueError: If the passed value is not in the correct format.
        """
        nums = re.findall(r'\d+', value)
        if len(nums) == 1:
            return float(nums[0])
        else:
            log.error(f'Invalid number found in trigger value: {value}')
            print(f'Invalid number found in trigger value: {value}')
            # if no trigger value available, exit
            raise ValueError(f'Invalid number found in trigger value: {value}')

    @staticmethod
    def find_operator_in_str(value) -> str:
        """Find the logic operator in a string.

        Args:
            value (str): Any value of the strategy.

        return:
            str: The operator in the string.

        raises:
            ValueError: If the passed value is not in the correct format.
        """
        nums = re.findall(r'\d+', value)
        if len(nums) == 1:
            return value.replace(str(nums[0]), '')
        else:
            log.error(f'Invalid number found in trigger value: {value}')
            print(f'Invalid number found in trigger value: {value}')
            # if no trigger value available, exit
            raise ValueError(f'Invalid number found in trigger value: {value}')
