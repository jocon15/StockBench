import logging

from StockBench.models.constants.general_constants import *
from StockBench.controllers.simulator.indicator.trigger import Trigger
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager
from StockBench.models.position.position import Position

log = logging.getLogger()


class StochasticTrigger(Trigger):
    # cannot use strategy symbol because it is "stochastic"
    DISPLAY_NAME = 'Stochastic'

    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=Trigger.AGNOSTIC)

    def calculate_additional_days_from_rule_key(self, rule_key: str, rule_value: any) -> int:
        rule_key_number_groups = list(map(int, self.find_all_nums_in_str(rule_key)))
        if rule_key_number_groups:
            return max(rule_key_number_groups)
        return DEFAULT_STOCHASTIC_LENGTH

    def calculate_additional_days_from_rule_value(self, rule_value: any) -> int:
        # logic for rule value is the same as the logic for rule key
        return self.calculate_additional_days_from_rule_key(rule_value, None)

    def add_indicator_data_from_rule_key(self, rule_key: str, rule_value: any, side: str, data_manager: DataManager):
        # ======== key based =========
        rule_key_number_groups = self.find_all_nums_in_str(rule_key)
        if len(rule_key_number_groups) > 0:
            num = int(rule_key_number_groups[0])
            self.__add_stochastic_to_simulation_data(num, data_manager)
        else:
            self.__add_stochastic_to_simulation_data(DEFAULT_STOCHASTIC_LENGTH, data_manager)
        # ======== value based (stochastic limit)=========
        rule_key_number_groups = self.find_all_nums_in_str(rule_value)
        if len(rule_key_number_groups) > 0:
            trigger_value = float(rule_key_number_groups[0])
            Trigger._add_trigger_value_as_column(f'{self.indicator_symbol}_{trigger_value}', trigger_value,
                                                 data_manager)

    def add_indicator_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        rule_key_number_groups = self.find_all_nums_in_str(rule_value)
        if len(rule_key_number_groups) > 0:
            num = int(rule_key_number_groups[0])
            self.__add_stochastic_to_simulation_data(num, data_manager)
        else:
            self.__add_stochastic_to_simulation_data(DEFAULT_STOCHASTIC_LENGTH, data_manager)

    def get_indicator_value_when_referenced(self, rule_value: str, data_manager: DataManager,
                                            current_day_index: int) -> float:
        # parse rule key will work even when passed a rule value
        return Trigger._parse_rule_key(rule_value, self.indicator_symbol, data_manager, current_day_index)

    def check_trigger(self, rule_key: str, rule_value: any, data_manager: DataManager, position: Position,
                      current_day_index: int) -> bool:
        log.debug(f'Checking stochastic algorithm: {rule_key}...')

        indicator_value = Trigger._parse_rule_key(rule_key, self.indicator_symbol, data_manager, current_day_index)

        log.debug(f'{self.DISPLAY_NAME} algorithm: {rule_key} checked successfully')

        return self.basic_trigger_check(indicator_value, rule_value)

    def __add_stochastic_to_simulation_data(self, length: int, data_manager: DataManager):
        """Adds the stochastic values to the simulation data."""
        # skip if there are stochastic values in the simulation data
        for col_name in data_manager.get_column_names():
            if self.indicator_symbol in col_name:
                return

        high_data = data_manager.get_column_data(data_manager.HIGH)
        low_data = data_manager.get_column_data(data_manager.LOW)
        close_data = data_manager.get_column_data(data_manager.CLOSE)
        stochastic_values = StochasticTrigger.calculate_stochastic_oscillator(length, high_data, low_data, close_data)

        data_manager.add_column(self.indicator_symbol, stochastic_values)

    @staticmethod
    def calculate_stochastic_oscillator(length: int, high_data: list, low_data: list, close_data: list) -> list:
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
