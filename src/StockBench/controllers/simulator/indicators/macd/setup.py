from typing import Union

from StockBench.controllers.simulator.indicator.exceptions import StrategyIndicatorError
from StockBench.controllers.simulator.indicator.setup_interface import SetupInterface
from StockBench.controllers.simulator.indicators.ema.setup import EMASetup
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager


class MACDSetup(SetupInterface):
    LARGE_EMA_LENGTH = 26
    SMALL_EMA_LENGTH = 12

    def __init__(self, strategy_symbol: str):
        super().__init__(strategy_symbol)

    def calculate_additional_days_from_rule_key(self, rule_key: str, rule_value: Union[str, int, dict, None]) -> int:
        return self.LARGE_EMA_LENGTH

    def calculate_additional_days_from_rule_value(self, rule_value: Union[str, int, dict]) -> int:
        return self.LARGE_EMA_LENGTH

    def add_indicator_data_from_rule_key(self, rule_key: str, rule_value: Union[str, int, dict, None], side: str,
                                         data_manager: DataManager):
        # if we already have MACD values in the df, we don't need to add them again
        for col_name in data_manager.get_column_names():
            if self.indicator_symbol == col_name:
                return

        price_data = data_manager.get_column_data(data_manager.CLOSE)

        data_manager.add_column(self.indicator_symbol, self.calculate_macd(price_data))

    def add_indicator_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        # logic for rule value is the same as the logic for rule key
        self.add_indicator_data_from_rule_key(rule_value, None, side, data_manager)

    def calculate_macd(self, price_data: list) -> list:
        """Calculates MACD values for a list of price values."""
        large_ema_length_values = EMASetup.calculate_ema(self.LARGE_EMA_LENGTH, price_data)

        small_ema_length_values = EMASetup.calculate_ema(self.SMALL_EMA_LENGTH, price_data)

        if len(large_ema_length_values) != len(small_ema_length_values):
            raise StrategyIndicatorError(f'{self.indicator_symbol} value lists for {self.indicator_symbol} must be the '
                                         f'same length!')

        macd_values = []
        for i in range(len(large_ema_length_values)):
            if large_ema_length_values[i] is None or small_ema_length_values[i] is None:
                # some early values of ema are None until sufficient data is available,
                # just set the MACD to None in these situations
                macd_values.append(None)
            else:
                macd_values.append(round(small_ema_length_values[i] - large_ema_length_values[i], 3))

        return macd_values
