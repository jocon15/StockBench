import re
import logging
from abc import abstractmethod
from typing import Tuple

from StockBench.constants import *
from StockBench.simulation_data.data_manager import DataManager
from StockBench.position.position import Position
from StockBench.indicator.exceptions import StrategyIndicatorError


log = logging.getLogger()


class Trigger:
    """Base class for an algorithm. Provides some shared functionality for an algorithm."""
    BUY = 0
    SELL = 1
    AGNOSTIC = 2

    def __init__(self, strategy_symbol: str, side: str):
        self.strategy_symbol = strategy_symbol
        self.__side = side

    def get_side(self):
        return self.__side

    @abstractmethod
    def additional_days(self, key: str, value: str) -> int:
        raise NotImplementedError('Additional days not implemented!')

    @abstractmethod
    def add_to_data(self, key: str, value: str, side: str, data_manager: DataManager):
        raise NotImplementedError('Add to data not implemented!')

    @abstractmethod
    def check_trigger(self, key: str, value: str, data_manager: DataManager, position: Position,
                      current_day_index: int) -> bool:
        raise NotImplementedError('Check algorithm not implemented!')

    def _parse_value(self, value: str, data_manager: DataManager, current_day_index: int) -> Tuple[str, float]:
        """Parser for parsing the operator and algorithm value from the value.

        NOTE: This is the default implementation for this, since it is used frequently in this form.
            For abnormal algorithm like candle colors, you can override this with another implementation.

        Args:
             value: The rule's value.
             data_manager: The simulation data manager.
             current_day_index: The current day index.

        returns:
            Tuple: The operator and the trigger value.
        """
        # find the operator and algorithm value (right hand side of the comparison)
        if CURRENT_PRICE_SYMBOL in value:
            trigger_value = float(data_manager.get_data_point(data_manager.CLOSE, current_day_index))
            operator = value.replace(CURRENT_PRICE_SYMBOL, '')
        else:
            trigger_value = self.find_single_numeric_in_str(value)
            operator = self.find_operator_in_str(value)

        return operator, trigger_value

    @staticmethod
    def basic_trigger_check(indicator_value: float, operator_value: str, trigger_value: float) -> bool:
        """Abstraction for basic algorithm comparison operators.

        Args:
            indicator_value: The value of the indicator.
            operator_value: The operator defined in the strategy
            trigger_value: The value of the algorithm.

        returns:
            bool: True if the algorithm was hit.
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
            if abs(indicator_value - trigger_value) <= 0.001:  # DOUBLE_COMPARISON_EPSILON
                return True
        return False

    @staticmethod
    def find_single_numeric_in_str(value: str) -> float:
        """Find a single numeric algorithm in a string.

        Args:
            value: Any value of the strategy.

        returns:
            float: The algorithm value in the string.

        raises:
            ValueError: If the passed value is not in the correct format (contains >1 or no numerics).
        """
        nums = re.findall(r'\d+', value)
        if len(nums) == 1:
            return float(nums[0])
        else:
            raise StrategyIndicatorError(f'Invalid amount of numbers found in algorithm value: {value}')

    @staticmethod
    def find_all_nums_in_str(value: str) -> list:
        """Finds all number groupings in a string.

        Args:
            value: The string to parse.

        returns:
            list: A list of numbers in the string.

        """
        return re.findall(r'\d+', value)

    @staticmethod
    def find_operator_in_str(value: str) -> str:
        """Find the logic operator in a string.

        Args:
            value: Any value of the strategy.

        returns:
            str: The operator in the string.

        raises:
            ValueError: If the passed value has incorrect amount of number groupings.
        """
        nums = re.findall(r'\d+', value)
        if len(nums) == 1:
            return value.replace(str(nums[0]), '')
        else:
            raise StrategyIndicatorError(f'Invalid amount of numbers found in algorithm value: {value}')

    @staticmethod
    def calculate_slope(y2: float, y1: float, length: int) -> float:
        """Calculate the slope between 2 points.

        Args:
            y2: The y-value of the final point.
            y1: The y-value of the initial point.
            length: The difference between the x-values of y2 and y1.

        returns:
            float: The slope between the two points.

        raises:
            ValueError: If the length is less than 2.
        """
        if length < 2:
            raise StrategyIndicatorError(f'Slope window length cannot be less than 2!')

        # calculate slope
        return round((y2 - y1) / float(length), 2)
