import logging
from StockBench.indicator.trigger import Trigger
from StockBench.indicator.exceptions import StrategyIndicatorError
from StockBench.simulation_data.data_manager import DataManager
from StockBench.position.position import Position
from StockBench.indicators.ema.ema import EMATrigger

log = logging.getLogger()


class MACDTrigger(Trigger):

    LARGE_EMA_LENGTH = 26

    SMALL_EMA_LENGTH = 12

    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=Trigger.AGNOSTIC)

    def additional_days_from_rule_key(self, rule_key, rule_value) -> int:
        """Calculate the additional days required.

        Args:
            rule_key (any): The key value from the strategy.
            rule_value (any): The value from the strategy.
        """
        return self.LARGE_EMA_LENGTH

    def add_to_data(self, rule_key, rule_value, side, data_manager):
        """Add data to the dataframe.

        Args:
            rule_key (any): The key value from the strategy.
            rule_value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (DataManager): The data object.
        """
        # if we already have MACD values in the df, we don't need to add them again
        for col_name in data_manager.get_column_names():
            if self.indicator_symbol == col_name:
                return

        price_data = data_manager.get_column_data(data_manager.CLOSE)

        data_manager.add_column(self.indicator_symbol, self.calculate_macd(price_data))

    def check_trigger(self, rule_key, rule_value, data_manager, position, current_day_index) -> bool:
        """Trigger logic for EMA.

        Args:
            rule_key (str): The key value of the algorithm.
            rule_value (str): The value of the algorithm.
            data_manager (DataManager): The data API object.
            position (Position): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if a trigger was hit.
        """
        log.debug(f'Checking {self.indicator_symbol} algorithm: {rule_key}...')

        indicator_value = Trigger._parse_rule_key_no_indicator_length(rule_key, self.indicator_symbol, data_manager,
                                                                      current_day_index)

        log.debug(f'{self.indicator_symbol} algorithm: {rule_key} checked successfully')

        return self.basic_trigger_check(indicator_value, rule_value, data_manager, current_day_index)

    def calculate_macd(self, price_data: list) -> list:
        """Calculate MACD values for a list of price values"""
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
