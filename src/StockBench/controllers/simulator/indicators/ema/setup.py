from typing import Union

from StockBench.controllers.simulator.indicator.exceptions import StrategyIndicatorError
from StockBench.controllers.simulator.indicator.setup_interface import SetupInterface
from StockBench.controllers.simulator.indicators.sma.trigger import SMATrigger
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager


class EMASetup(SetupInterface):
    def __init__(self, strategy_symbol: str):
        super().__init__(strategy_symbol)

    def calculate_additional_days_from_rule_key(self, rule_key: str, rule_value: Union[str, int, dict, None]) -> int:
        rule_key_number_groups = list(map(int, self.find_all_nums_in_str(rule_key)))
        if rule_key_number_groups:
            return max(rule_key_number_groups)
        raise StrategyIndicatorError(f'{self.indicator_symbol} indicator must have an indicator length!')

    def calculate_additional_days_from_rule_value(self, rule_value: Union[str, int, dict]) -> int:
        # logic for rule value is the same as the logic for rule key
        return self.calculate_additional_days_from_rule_key(str(rule_value), None)

    def add_indicator_data_from_rule_key(self, rule_key: str, rule_value: Union[str, int, dict, None], side: str,
                                         data_manager: DataManager):
        nums = self.find_all_nums_in_str(rule_key)
        if len(nums) > 0:
            indicator_length = int(nums[0])
            self.__add_ema_to_simulation_data(indicator_length, data_manager)
        else:
            raise StrategyIndicatorError(f'{self.indicator_symbol} key: {rule_key} must have an indicator length!')

    def add_indicator_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        # logic for rule value is the same as the logic for rule key
        self.add_indicator_data_from_rule_key(rule_value, None, side, data_manager)

    def __add_ema_to_simulation_data(self, length: int, data_manager: DataManager):
        """Adds EMA indicator data to the simulation data."""
        column_title = f'{self.indicator_symbol}{length}'

        # skip if there are EMA values in the simulation data
        for col_name in data_manager.get_column_names():
            if column_title in col_name:
                return

        price_data = data_manager.get_column_data(data_manager.CLOSE)
        ema_values = self.calculate_ema(length, price_data)

        data_manager.add_column(column_title, ema_values)

    @staticmethod
    def calculate_ema(length: int, price_data: list) -> list:
        """Calculates the EMA values for a list of price values."""
        k = 2 / (length + 1)

        # get the initial ema value (uses sma of length days)
        previous_ema = SMATrigger.calculate_sma(length, price_data[0:length])[-1]

        ema_values = []
        for i in range(len(price_data)):
            if i < length:
                ema_values.append(None)
            else:
                ema_point = round((k * (float(price_data[i]) - previous_ema)) + previous_ema, 3)
                ema_values.append(ema_point)
                previous_ema = ema_point
        return ema_values
