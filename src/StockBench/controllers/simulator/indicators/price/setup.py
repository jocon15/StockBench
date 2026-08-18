from typing import Union

from StockBench.controllers.simulator.indicator.setup_interface import SetupInterface
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager


class PriceSetup(SetupInterface):
    def __init__(self, strategy_symbol: str):
        super().__init__(strategy_symbol)

    def calculate_additional_days_from_rule_key(self, rule_key: str, rule_value: Union[str, int, dict, None]) -> int:
        return 0

    def calculate_additional_days_from_rule_value(self, rule_value: Union[str, int, dict]) -> int:
        return 0

    def add_indicator_data_from_rule_key(self, rule_key: str, rule_value: Union[str, int, dict], side: str,
                                         data_manager: DataManager):
        # price is in the data by default, no need to add it
        return

    def add_indicator_data_from_rule_value(self, rule_value: str, side: str,
                                           data_manager: DataManager):
        # price is in the data by default, no need to add it
        return
