import re
from abc import ABC, abstractmethod
from typing import Union

from StockBench.controllers.simulator.indicator.exceptions import NoThresholdFoundException
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager


class SetupInterface(ABC):
    OPERATORS = ['<=', '>=', '<', '>', '=']

    def __init__(self, indicator_symbol: str):
        self.indicator_symbol = indicator_symbol

    @abstractmethod
    def calculate_additional_days_from_rule_key(self, rule_key: str, rule_value: Union[str, int, dict, None]) -> int:
        """Calculates the additional days required from a rule key and a rule value."""
        # Must include rule value as a parameter because some triggers (candlestick) cannot deduce indicator length from
        # the rule key and cannot be identified from the rule value.
        raise NotImplementedError('Additional days from rule key not implemented!')

    @abstractmethod
    def calculate_additional_days_from_rule_value(self, rule_value: Union[str, int, dict]) -> int:
        """Calculates the additional days required from a rule value."""
        raise NotImplementedError('Additional days from rule value not implemented!')

    @abstractmethod
    def add_indicator_data_from_rule_key(self, rule_key: str, rule_value: Union[str, int, dict], side: str,
                                         data_manager: DataManager):
        """Adds the indicator data to the simulation data from a rule key."""
        # Must include rule value as a parameter because oscillator triggers (RSI, stochastic,...) have literal
        # threshold values in the rule value that need to be added to the data. Literal threshold values cannot be
        # identified with only the rule value, which is why we pass them in as a parameter.
        # "by_rule_key" just implies that the rule key was responsible for identifying the trigger type via the mathing
        # indicator's strategy name
        raise NotImplementedError('Add to data from rule key not implemented!')

    @abstractmethod
    def add_indicator_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        """Adds the indicator data to the simulation data from a rule value."""
        raise NotImplementedError('Add to data not implemented!')

    def get_threshold_from_rule_value(self, rule_value: str) -> float:
        for operator in self.OPERATORS:
            if operator in str(rule_value):
                rule_value_stripped = str(rule_value).strip(operator)
                try:
                    return float(str(rule_value_stripped))
                except ValueError:
                    raise NoThresholdFoundException()
        raise NoThresholdFoundException()

    @staticmethod
    def find_all_nums_in_str(rule_value: str) -> list:
        """Finds all number groupings in a rule value string."""
        return re.findall(r'\d+(?:\.\d+)?', rule_value)
