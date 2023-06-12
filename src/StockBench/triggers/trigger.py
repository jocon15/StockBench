import re
import logging
from abc import abstractmethod

log = logging.getLogger()


class Trigger:
    def __init__(self, strategy_symbol):
        self.strategy_symbol = strategy_symbol

    @abstractmethod
    def check_trigger(self, _key, _value, data_obj, position_obj, current_day_index) -> bool:
        raise NotImplementedError('check trigger not implemented!')

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
        nums = re.findall(r'\d+', value)
        if len(nums) == 1:
            return value.replace(str(nums[0]), '')
        else:
            log.error(f'Invalid number found in trigger value: {value}')
            print(f'Invalid number found in trigger value: {value}')
            # if no trigger value available, exit
            raise ValueError(f'Invalid number found in trigger value: {value}')
