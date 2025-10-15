import logging

from StockBench.controllers.simulator.indicator import Trigger
from StockBench.controllers.simulator.indicator import StrategyIndicatorError
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager
from StockBench.models.position.position import Position
from StockBench.indicators.ema.ema import EMATrigger

log = logging.getLogger()


class MACDTrigger(Trigger):
    LARGE_EMA_LENGTH = 26
    SMALL_EMA_LENGTH = 12

    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=Trigger.AGNOSTIC)

    def calculate_additional_days_from_rule_key(self, rule_key: str, rule_value: any) -> int:
        return self.LARGE_EMA_LENGTH

    def calculate_additional_days_from_rule_value(self, rule_value: any) -> int:
        return self.LARGE_EMA_LENGTH

    def add_indicator_data_from_rule_key(self, rule_key: str, rule_value: any, side: str, data_manager: DataManager):
        # if we already have MACD values in the df, we don't need to add them again
        for col_name in data_manager.get_column_names():
            if self.indicator_symbol == col_name:
                return

        price_data = data_manager.get_column_data(data_manager.CLOSE)

        data_manager.add_column(self.indicator_symbol, self.calculate_macd(price_data))

    def add_indicator_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        # logic for rule value is the same as the logic for rule key
        return self.add_indicator_data_from_rule_key(rule_value, None, side, data_manager)

    def get_indicator_value_when_referenced(self, rule_value: str, data_manager: DataManager,
                                            current_day_index: int) -> float:
        # parse rule key will work even when passed a rule value
        return Trigger._parse_rule_key_no_indicator_length(rule_value, self.indicator_symbol, data_manager,
                                                           current_day_index)

    def check_trigger(self, rule_key: str, rule_value: any, data_manager: DataManager, position: Position,
                      current_day_index: int) -> bool:
        log.debug(f'Checking {self.indicator_symbol} algorithm: {rule_key}...')

        indicator_value = Trigger._parse_rule_key_no_indicator_length(rule_key, self.indicator_symbol, data_manager,
                                                                      current_day_index)

        log.debug(f'{self.indicator_symbol} algorithm: {rule_key} checked successfully')

        return self.basic_trigger_check(indicator_value, rule_value)

    def calculate_macd(self, price_data: list) -> list:
        """Calculates MACD values for a list of price values."""
        large_ema_length_values = EMATrigger.calculate_ema(self.LARGE_EMA_LENGTH, price_data)

        small_ema_length_values = EMATrigger.calculate_ema(self.SMALL_EMA_LENGTH, price_data)

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
