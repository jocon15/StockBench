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

    def __init__(self, indicator_symbol: str, side: str):
        self.indicator_symbol = indicator_symbol
        self.__side = side

    def get_side(self):
        return self.__side

    @abstractmethod
    def additional_days_from_rule_key(self, rule_key: str, rule_value: any) -> int:
        # must include rule value as a parameter because some triggers (candlestick) cannot deduce indicator length from
        # the rule key and cannot be identified from the rule value
        raise NotImplementedError('Additional days from rule key not implemented!')

    @abstractmethod
    def additional_days_from_rule_value(self, rule_value: any) -> int:
        raise NotImplementedError('Additional days from rule value not implemented!')

    @abstractmethod
    def add_to_data_from_rule_key(self, rule_key: str, side: str, data_manager: DataManager):
        # candlestick does not need rule value here because candlestick does not have any add to data logic
        raise NotImplementedError('Add to data from rule key not implemented!')

    @abstractmethod
    def add_to_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        raise NotImplementedError('Add to data not implemented!')

    @abstractmethod
    def check_trigger(self, rule_key: str, rule_value: any, data_manager: DataManager, position: Position,
                      current_day_index: int) -> bool:
        raise NotImplementedError('Check algorithm from rule value not implemented!')

    def _parse_rule_value(self, rule_value: str, data_manager: DataManager,
                          current_day_index: int) -> Tuple[str, float]:
        """Parser for parsing the operator and algorithm value from the value.

        NOTE: This is the default implementation for this, since it is used frequently in this form.
            For abnormal algorithm like candle colors, you can override this with another implementation.

        Args:
             rule_value: The rule's value.
             data_manager: The simulation data manager.
             current_day_index: The current day index.

        returns:
            Tuple: The operator and the trigger value.
        """
        # find the operator and algorithm value (right hand side of the comparison)
        if CURRENT_PRICE_SYMBOL in rule_value:
            trigger_value = float(data_manager.get_data_point(data_manager.CLOSE, current_day_index))
            operator = rule_value.replace(CURRENT_PRICE_SYMBOL, '')
        else:
            trigger_value = self.find_single_numeric_in_str(rule_value)
            operator = self.find_operator_in_str(rule_value)

        return operator, trigger_value

    def basic_trigger_check(self, indicator_value: float, rule_value: str, data_manager: DataManager,
                            current_day_index: int) -> bool:
        """Basic trigger check with comparison operators."""
        operator, trigger_value = self._parse_rule_value(rule_value, data_manager, current_day_index)

        if operator == '<=':
            if indicator_value <= trigger_value:
                return True
        elif operator == '>=':
            if indicator_value >= trigger_value:
                return True
        elif operator == '<':
            if indicator_value < trigger_value:
                return True
        elif operator == '>':
            if indicator_value > trigger_value:
                return True
        elif operator == '=':
            if abs(indicator_value - trigger_value) <= 0.001:  # DOUBLE_COMPARISON_EPSILON
                return True
        return False

    @staticmethod
    def _parse_rule_key(rule_key: str, indicator_symbol: str, data_manager: DataManager,
                        current_day_index: int) -> float:
        """Translates a complex rule key for an indicator value where the indicator has a default value.
        Can have 0, 1, or 2 number groupings.
        """
        rule_key_number_groups = Trigger.find_all_nums_in_str(rule_key)
        if len(rule_key_number_groups) == 0:
            # rule key does not define an indicator length (use default)
            if SLOPE_SYMBOL in rule_key:
                raise StrategyIndicatorError(f'{indicator_symbol} rule key: {rule_key} does not contain '
                                             f'enough number groupings!')
            indicator_value = float(data_manager.get_data_point(indicator_symbol, current_day_index))
        elif len(rule_key_number_groups) == 1:
            if SLOPE_SYMBOL in rule_key:
                # make sure the number is after the slope emblem and not the RSI emblem
                if rule_key.split(str(rule_key_number_groups))[0] == indicator_symbol + SLOPE_SYMBOL:
                    raise StrategyIndicatorError(f'{indicator_symbol} rule key: {rule_key} does not contain '
                                                 f'a slope value!')
            # rule key defines an indicator length (not using default)
            column_title = f'{indicator_symbol}{int(rule_key_number_groups[0])}'
            indicator_value = float(data_manager.get_data_point(column_title, current_day_index))
        elif len(rule_key_number_groups) == 2:
            column_title = f'{indicator_symbol}{int(rule_key_number_groups[0])}'
            # 2 number groupings suggests the $slope indicator is being used
            if SLOPE_SYMBOL in rule_key:
                indicator_value = Trigger.__slope_value(column_title, int(rule_key_number_groups[1]), current_day_index,
                                                        data_manager)
            else:
                raise StrategyIndicatorError(f'{indicator_symbol} rule key: {rule_key} contains too many number '
                                             f'groupings! Are you missing a $slope emblem?')
        else:
            raise StrategyIndicatorError(f'{indicator_symbol} rule key: {rule_key} contains invalid number '
                                         f'groupings!')

        return indicator_value

    @staticmethod
    def _parse_rule_key_no_default_indicator_length(rule_key: str, indicator_symbol: str, data_manager: DataManager,
                                                    current_day_index: int) -> float:
        """Translates a complex rule key for an indicator value where the indicator DOES NOT have a default value.
        Can have 1, or 2 number groupings.
        """
        rule_key_number_groups = Trigger.find_all_nums_in_str(rule_key)

        if len(rule_key_number_groups) == 1:
            if SLOPE_SYMBOL in rule_key:
                raise StrategyIndicatorError(f'{indicator_symbol} rule key: {rule_key} does not contain '
                                             f'enough number groupings!')
            column_title = f'{indicator_symbol}{int(rule_key_number_groups[0])}'
            indicator_value = float(data_manager.get_data_point(column_title, current_day_index))
        elif len(rule_key_number_groups) == 2:
            column_title = f'{indicator_symbol}{int(rule_key_number_groups[0])}'
            # 2 number groupings suggests the $slope indicator is being used
            if SLOPE_SYMBOL in rule_key:
                indicator_value = Trigger.__slope_value(column_title, int(rule_key_number_groups[1]), current_day_index,
                                                        data_manager)
            else:
                raise StrategyIndicatorError(f'{indicator_symbol} rule key: {rule_key} contains too many number '
                                             f'groupings! Are you missing a $slope emblem?')
        else:
            raise StrategyIndicatorError(f'{indicator_symbol} rule key: {rule_key} contains invalid number '
                                         f'groupings!')

        return indicator_value

    @staticmethod
    def _parse_rule_key_no_indicator_length(rule_key: str, indicator_symbol: str, data_manager: DataManager,
                                            current_day_index: int) -> float:
        """Parser for parsing the key into the indicator value."""
        rule_key_number_groups = Trigger.find_all_nums_in_str(rule_key)

        # MACD can only have slope emblem therefore 1 or 0 number groupings are acceptable
        if len(rule_key_number_groups) == 0:
            if SLOPE_SYMBOL in rule_key:
                raise StrategyIndicatorError(f'{indicator_symbol} rule key: {rule_key} does not contain'
                                             f' enough number groupings!')
            indicator_value = float(data_manager.get_data_point(indicator_symbol, current_day_index))
        elif len(rule_key_number_groups) == 1:
            # 1 number grouping suggests the $slope indicator is being used
            if SLOPE_SYMBOL in rule_key:
                indicator_value = Trigger.__slope_value(indicator_symbol, int(rule_key_number_groups[0]),
                                                        current_day_index, data_manager)
            else:
                raise StrategyIndicatorError(f'{indicator_symbol} rule key: {rule_key} contains too many number '
                                             f'groupings! Are you missing a $slope emblem?')
        else:
            raise StrategyIndicatorError(f'{indicator_symbol} rule key: {rule_key} contains '
                                         f'invalid number groupings!')

        return indicator_value

    @staticmethod
    def _add_trigger_column(column_name: str, trigger_value: float, data_manager: DataManager):
        """Add a trigger value to the df."""
        # if we already have an RSI trigger column with this value in the df, we don't need to add it again
        for col_name in data_manager.get_column_names():
            if column_name == col_name:
                return

        list_values = [trigger_value for _ in range(data_manager.get_data_length())]

        data_manager.add_column(column_name, list_values)

    @staticmethod
    def find_single_numeric_in_str(rule_value: str) -> float:
        """Find a single numeric algorithm in a string.

        Args:
            rule_value: Any value of the strategy.

        returns:
            float: The algorithm value in the string.

        raises:
            ValueError: If the passed value is not in the correct format (contains >1 or no numerics).
        """
        nums = re.findall(r'\d+(?:\.\d+)?', rule_value)
        if len(nums) == 1:
            return float(nums[0])
        else:
            raise StrategyIndicatorError(f'Invalid amount of numbers found in algorithm value: {rule_value}')

    @staticmethod
    def find_all_nums_in_str(rule_value: str) -> list:
        """Finds all number groupings in a string.

        Args:
            rule_value: The string to parse.

        returns:
            list: A list of numbers in the string.

        """
        return re.findall(r'\d+(?:\.\d+)?', rule_value)

    @staticmethod
    def find_operator_in_str(rule_value: str) -> str:
        """Find the logic operator in a string.

        Args:
            rule_value: Any value of the strategy.

        returns:
            str: The operator in the string.

        raises:
            ValueError: If the passed value has incorrect amount of number groupings.
        """
        nums = re.findall(r'\d+(?:\.\d+)?', rule_value)
        if len(nums) == 1:
            return rule_value.replace(str(nums[0]), '')
        else:
            raise StrategyIndicatorError(f'Invalid amount of numbers found in algorithm value: {rule_value}')

    @staticmethod
    def __slope_value(column_title: str, slope_window_length: int, current_day_index: int,
                      data_manager: DataManager) -> float:
        """Gets a slope value for an indicator."""
        # data request length is window - 1 to account for the current day index being a part of the window
        slope_data_request_length = slope_window_length - 1

        return Trigger.calculate_slope(
            float(data_manager.get_data_point(column_title, current_day_index)),
            float(data_manager.get_data_point(column_title, current_day_index - slope_data_request_length)),
            slope_window_length
        )

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
