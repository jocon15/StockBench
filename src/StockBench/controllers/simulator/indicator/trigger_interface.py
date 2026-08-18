import re
import logging
from abc import ABC, abstractmethod
from typing import Tuple, Union

from StockBench.models.constants.general_constants import *
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager
from StockBench.models.position.position import Position
from StockBench.controllers.simulator.indicator.exceptions import StrategyIndicatorError

log = logging.getLogger()


class TriggerInterface(ABC):
    """Base class for an indicator trigger."""
    BUY = 0
    SELL = 1
    AGNOSTIC = 2

    def __init__(self, indicator_symbol: str, side: int):
        self.indicator_symbol = indicator_symbol
        self.__side = side

    def get_side(self):
        return self.__side

    @abstractmethod
    def get_indicator_value_when_referenced(self, rule_value: str, data_manager: DataManager,
                                            current_day_index: int) -> float:
        """Gets the value of the indicator when referenced in another rule."""
        raise NotImplementedError('Get value when referenced not implemented!')

    @abstractmethod
    def check_trigger(self, rule_key: str, rule_value: Union[str, int, dict], data_manager: DataManager,
                      position: Position, current_day_index: int) -> bool:
        """Evaluate the trigger for a trigger event."""
        raise NotImplementedError('Check algorithm from rule value not implemented!')

    def basic_trigger_check(self, indicator_value: float, rule_value: str) -> bool:
        """Basic trigger check with comparison operators."""
        operator, trigger_value = self._parse_rule_value(rule_value)

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
    def find_single_numeric_in_str(rule_value: str) -> float:
        """Finds a single numeric value in a rule value string."""
        nums = re.findall(r'\d+(?:\.\d+)?', rule_value)
        if len(nums) == 1:
            return float(nums[0])
        else:
            raise StrategyIndicatorError(f'Invalid amount of numbers found in algorithm value: {rule_value}')

    @staticmethod
    def find_all_nums_in_str(rule_value: str) -> list:
        """Finds all number groupings in a rule value string."""
        return re.findall(r'\d+(?:\.\d+)?', rule_value)

    @staticmethod
    def find_operator_in_str(rule_value: str) -> str:
        """Finds the logic operator in a rule value string."""
        nums = re.findall(r'\d+(?:\.\d+)?', rule_value)
        if len(nums) == 1:
            return rule_value.replace(str(nums[0]), '')
        else:
            raise StrategyIndicatorError(f'Invalid amount of numbers found in algorithm value: {rule_value}')

    @staticmethod
    def parse_rule_key(rule_key: str, indicator_symbol: str, data_manager: DataManager,
                       current_day_index: int) -> float:
        """Parses a rule key for an indicator value."""
        rule_key_number_groups = TriggerInterface.find_all_nums_in_str(rule_key)
        if len(rule_key_number_groups) == 0:
            indicator_value = TriggerInterface.__parse_rule_key_0_number_groupings(rule_key, rule_key_number_groups,
                                                                                   indicator_symbol, data_manager,
                                                                                   current_day_index)
        elif len(rule_key_number_groups) == 1:
            indicator_value = TriggerInterface.__parse_rule_key_1_number_grouping(rule_key, rule_key_number_groups,
                                                                                  indicator_symbol, data_manager,
                                                                                  current_day_index)
        elif len(rule_key_number_groups) == 2:
            indicator_value = TriggerInterface.__parse_rule_key_2_number_groupings(rule_key, rule_key_number_groups,
                                                                                   indicator_symbol, data_manager,
                                                                                   current_day_index)
        else:
            raise StrategyIndicatorError(f'{indicator_symbol} rule key: {rule_key} contains invalid number '
                                         f'groupings!')

        return indicator_value

    def _parse_rule_value(self, rule_value: str) -> Tuple[str, float]:
        """Parses a rule value for an operator and a trigger value from a rule value."""
        return self.find_operator_in_str(rule_value), self.find_single_numeric_in_str(rule_value)

    @staticmethod
    def parse_rule_key_no_default_indicator_length(rule_key: str, indicator_symbol: str, data_manager: DataManager,
                                                   current_day_index: int) -> float:
        """Parses a rule key for an indicator value where the indicator DOES NOT have a default value."""
        rule_key_number_groups = TriggerInterface.find_all_nums_in_str(rule_key)

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
                indicator_value = TriggerInterface.__calculate_slope(column_title, int(rule_key_number_groups[1]),
                                                                     current_day_index,
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
                                            current_day_index: int, alt_data_access_key: str = None) -> float:
        """Parses a rule key for an indicator value with no indicator length.

        Alt data access key is used for triggers like price where the indicator in the strategy is "Price" but the
        column in the data is called "Close". In this case "Close" would be the alt data access key.
        """
        if alt_data_access_key:
            column_title = alt_data_access_key
        else:
            column_title = indicator_symbol

        rule_key_number_groups = TriggerInterface.find_all_nums_in_str(rule_key)

        # ex: MACD can only have slope emblem therefore 1 or 0 number groupings are acceptable
        if len(rule_key_number_groups) == 0:
            if SLOPE_SYMBOL in rule_key:
                raise StrategyIndicatorError(f'{indicator_symbol} rule key: {rule_key} does not contain'
                                             f' enough number groupings!')
            indicator_value = float(data_manager.get_data_point(column_title, current_day_index))
        elif len(rule_key_number_groups) == 1:
            # 1 number grouping suggests the $slope indicator is being used
            if SLOPE_SYMBOL in rule_key:
                indicator_value = TriggerInterface.__calculate_slope(column_title, int(rule_key_number_groups[0]),
                                                                     current_day_index, data_manager)
            else:
                raise StrategyIndicatorError(f'{indicator_symbol} rule key: {rule_key} contains too many number '
                                             f'groupings! Are you missing a $slope emblem?')
        else:
            raise StrategyIndicatorError(f'{indicator_symbol} rule key: {rule_key} contains '
                                         f'invalid number groupings!')

        return indicator_value

    @staticmethod
    def __parse_rule_key_0_number_groupings(rule_key: str, rule_key_number_groups: list, indicator_symbol: str,
                                            data_manager: DataManager, current_day_index: int) -> float:
        """Parses a rule key with 0 number groupings for an indicator value."""
        # rule key does not define an indicator length (use default)
        if SLOPE_SYMBOL in rule_key:
            raise StrategyIndicatorError(f'{indicator_symbol} rule key: {rule_key} does not contain '
                                         f'enough number groupings!')
        return float(data_manager.get_data_point(indicator_symbol, current_day_index))

    @staticmethod
    def __parse_rule_key_1_number_grouping(rule_key: str, rule_key_number_groups: list, indicator_symbol: str,
                                           data_manager: DataManager, current_day_index: int) -> float:
        """Parses a rule key with 1 number grouping for an indicator value."""
        if SLOPE_SYMBOL in rule_key:
            # make sure the number is after the slope emblem and not the indicator emblem
            if rule_key.split(str(rule_key_number_groups))[0] == indicator_symbol + SLOPE_SYMBOL:
                raise StrategyIndicatorError(f'{indicator_symbol} rule key: {rule_key} does not contain '
                                             f'a slope value!')
        # rule key defines an indicator length (not using default)
        column_title = f'{indicator_symbol}{int(rule_key_number_groups[0])}'
        return float(data_manager.get_data_point(column_title, current_day_index))

    @staticmethod
    def __parse_rule_key_2_number_groupings(rule_key: str, rule_key_number_groups: list, indicator_symbol: str,
                                            data_manager: DataManager, current_day_index: int) -> float:
        """Parses a rule key with 2 number groupings for an indicator value."""
        column_title = f'{indicator_symbol}{int(rule_key_number_groups[0])}'
        # 2 number groupings suggests the $slope indicator is being used
        if SLOPE_SYMBOL in rule_key:
            return TriggerInterface.__calculate_slope(column_title, int(rule_key_number_groups[1]),
                                                      current_day_index, data_manager)
        else:
            raise StrategyIndicatorError(f'{indicator_symbol} rule key: {rule_key} contains too many number '
                                         f'groupings! Are you missing a $slope emblem?')

    @staticmethod
    def __calculate_slope(column_title: str, slope_window_length: int, current_day_index: int,
                          data_manager: DataManager) -> float:
        """Calculates a slope value from the current day to some previous day."""
        # data request length is window - 1 to account for the current day index being a part of the window
        slope_data_request_length = slope_window_length - 1

        return TriggerInterface.__calculate_point_slope(
            float(data_manager.get_data_point(column_title, current_day_index)),
            float(data_manager.get_data_point(column_title, current_day_index - slope_data_request_length)),
            slope_window_length
        )

    @staticmethod
    def __calculate_point_slope(y2: float, y1: float, length: int) -> float:
        """Calculates the slope between 2 points."""
        if length < 2:
            raise StrategyIndicatorError(f'Slope window length cannot be less than 2!')

        return round((y2 - y1) / float(length), 2)
