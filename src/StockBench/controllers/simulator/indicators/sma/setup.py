import statistics
from typing import Union

from StockBench.controllers.simulator.indicator.exceptions import StrategyIndicatorError
from StockBench.controllers.simulator.indicator.setup_interface import SetupInterface
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager


class SMASetup(SetupInterface):
    def __init__(self, strategy_symbol: str):
        super().__init__(strategy_symbol)

    def calculate_additional_days_from_rule_key(self, rule_key: str, rule_value: Union[str, int, dict, None]) -> int:
        rule_key_number_groups = list(map(int, self.find_all_nums_in_str(rule_key)))
        if rule_key_number_groups:
            return max(rule_key_number_groups)
        raise StrategyIndicatorError(f'{self.indicator_symbol} rule key: {rule_key} must have an indicator length!')

    def calculate_additional_days_from_rule_value(self, rule_value: Union[str, int, dict]) -> int:
        # logic for rule value is the same as the logic for rule key
        return self.calculate_additional_days_from_rule_key(str(rule_value), None)

    def add_indicator_data_from_rule_key(self, rule_key: str, rule_value: Union[str, int, dict, None], side: str,
                                         data_manager: DataManager):
        rule_key_number_groups = self.find_all_nums_in_str(rule_key)
        if len(rule_key_number_groups) > 0:
            indicator_length = int(rule_key_number_groups[0])
            self.__add_sma_to_simulation_data(indicator_length, data_manager)
        else:
            raise StrategyIndicatorError(f'{self.indicator_symbol} rule key: {rule_key} must have an indicator length!')

    def add_indicator_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        # logic for rule value is the same as the logic for rule key
        self.add_indicator_data_from_rule_key(rule_value, None, side, data_manager)

    def __add_sma_to_simulation_data(self, length: int, data_manager: DataManager):
        """Adds SMA indicator values to the simulation data."""
        column_title = f'{self.indicator_symbol}{length}'

        # if SMA values ar already in the df, we don't need to add them again
        for col_name in data_manager.get_column_names():
            if column_title in col_name:
                return

        price_data = data_manager.get_column_data(data_manager.CLOSE)
        sma_values = self.calculate_sma(length, price_data)

        data_manager.add_column(column_title, sma_values)

    @staticmethod
    def calculate_sma(length: int, price_data: list) -> list:
        """Calculates the SMA values for a list of price values."""
        price_values = []
        sma_values = []
        all_sma_values = []
        for element in price_data:
            if len(price_values) < length:
                price_values.append(float(element))
            else:
                price_values.pop(0)
                sma_values.pop(0)
                price_values.append(float(element))
            avg = round(statistics.mean(price_values), 3)
            sma_values.append(avg)
            all_sma_values.append(avg)
        return all_sma_values
