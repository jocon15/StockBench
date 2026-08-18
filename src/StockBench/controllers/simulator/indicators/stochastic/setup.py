from typing import Union

from StockBench.controllers.simulator.indicator.exceptions import NoThresholdFoundException
from StockBench.controllers.simulator.indicator.setup_interface import SetupInterface
from StockBench.models.constants.general_constants import *
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager


class StochasticSetup(SetupInterface):
    def __init__(self, strategy_symbol: str):
        super().__init__(strategy_symbol)

    def calculate_additional_days_from_rule_key(self, rule_key: str, rule_value: Union[str, int, dict, None]) -> int:
        rule_key_number_groups = list(map(int, self.find_all_nums_in_str(rule_key)))
        if rule_key_number_groups:
            return max(rule_key_number_groups)
        return DEFAULT_STOCHASTIC_LENGTH

    def calculate_additional_days_from_rule_value(self, rule_value: Union[str, int, dict]) -> int:
        # logic for rule value is the same as the logic for rule key
        return self.calculate_additional_days_from_rule_key(str(rule_value), None)

    def add_indicator_data_from_rule_key(self, rule_key: str, rule_value: Union[str, int, dict], side: str,
                                         data_manager: DataManager):
        # assume stochastic was found in the rule key
        # ======== key based =========
        rule_key_number_groups = self.find_all_nums_in_str(rule_key)
        if len(rule_key_number_groups) > 0:
            num = int(rule_key_number_groups[0])
            self.__add_stochastic_to_simulation_data(num, data_manager)
        else:
            self.__add_stochastic_to_simulation_data(DEFAULT_STOCHASTIC_LENGTH, data_manager)
        # ======== value based (stochastic thresholds) =========
        # add threshold to data for charting if the rule value is an operator and a float value combined
        try:
            threshold_value = self.get_threshold_from_rule_value(str(rule_value))
        except NoThresholdFoundException:
            # rule value is not a threshold, done here
            return

        # NOTE: this column name is JUST for charting purposes and NOT for trigger purposes
        # column name is in "stochastic_xx.x"format
        self.add_trigger_value_as_column(f'{self.indicator_symbol}_{threshold_value}',
                                                     threshold_value, data_manager)

    def add_indicator_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        # assume stochastic was found in the rule value
        rule_value_number_groups = self.find_all_nums_in_str(rule_value)
        if len(rule_value_number_groups) > 0:
            num = int(rule_value_number_groups[0])
            self.__add_stochastic_to_simulation_data(num, data_manager)
        else:
            self.__add_stochastic_to_simulation_data(DEFAULT_STOCHASTIC_LENGTH, data_manager)

    def __add_stochastic_to_simulation_data(self, length: int, data_manager: DataManager):
        """Adds the stochastic values to the simulation data."""
        if length == DEFAULT_STOCHASTIC_LENGTH:
            column_title = self.indicator_symbol
        else:
            column_title = f"{self.indicator_symbol}{length}"

        # skip if there are stochastic values in the simulation data
        for col_name in data_manager.get_column_names():
            # since this indicator supports custom lengths it is direct equality, not contains
            if column_title == col_name:
                return

        high_data = data_manager.get_column_data(data_manager.HIGH)
        low_data = data_manager.get_column_data(data_manager.LOW)
        close_data = data_manager.get_column_data(data_manager.CLOSE)
        stochastic_values = self.__calculate_stochastic_oscillator(length, high_data, low_data, close_data)

        data_manager.add_column(column_title, stochastic_values)

    @staticmethod
    def __calculate_stochastic_oscillator(length: int, high_data: list, low_data: list, close_data: list) -> list:
        """Calculates stochastic oscillator values for a list of price values."""
        past_length_days_high = []
        past_length_days_low = []
        past_length_days_close = []
        stochastic_oscillator = []
        for i in range(len(close_data)):
            if i < length:
                past_length_days_high.append(float(high_data[i]))
                past_length_days_low.append(float(low_data[i]))
                past_length_days_close.append(float(close_data[i]))
            else:
                past_length_days_high.pop(0)
                past_length_days_low.pop(0)
                past_length_days_close.pop(0)
                past_length_days_high.append(float(high_data[i]))
                past_length_days_low.append(float(low_data[i]))
                past_length_days_close.append(float(close_data[i]))

            stochastic_oscillator.append(round(((float(close_data[i]) - min(past_length_days_low)) /
                                                (max(past_length_days_high) - min(past_length_days_low))) * 100.0, 3))

        return stochastic_oscillator
