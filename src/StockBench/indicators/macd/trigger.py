import logging
import statistics
from StockBench.constants import *
from StockBench.indicator.trigger import Trigger
from StockBench.indicator.exceptions import StrategyIndicatorError
from StockBench.simulation_data.data_manager import DataManager
from StockBench.position.position import Position

log = logging.getLogger()


class MACDTrigger(Trigger):

    LARGE_EMA_LENGTH = 26

    SMALL_EMA_LENGTH = 12

    DATA_COLUMN_TITLE = 'MACD'

    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol, side=Trigger.AGNOSTIC)

    def additional_days(self, rule_key, value_value) -> int:
        """Calculate the additional days required.

        Args:
            rule_key (any): The key value from the strategy.
            value_value (any): The value from the strategy.
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
            if self.DATA_COLUMN_TITLE == col_name:
                return

        price_data = data_manager.get_column_data(data_manager.CLOSE)

        data_manager.add_column(self.DATA_COLUMN_TITLE, self.__calculate_macd(price_data))

    def check_trigger(self, rule_key, rule_value, data_manager, position, current_day_index) -> bool:
        """Trigger logic for EMA.

        Args:
            rule_key (str): The key value of the algorithm.
            rule_value (str): The value of the algorithm.
            data_manager (DataManager): The data API object.
            position (Position): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the algorithm was hit.
        """
        log.debug(f'Checking {self.strategy_symbol} algorithm: {rule_key}...')

        indicator_value = self.__parse_key(rule_key, data_manager, current_day_index)

        operator, trigger_value = self._parse_rule_value(rule_value, data_manager, current_day_index)

        log.debug(f'{self.strategy_symbol} algorithm: {rule_key} checked successfully')

        return Trigger.basic_trigger_check(indicator_value, operator, trigger_value)

    def __parse_key(self, rule_key: str, data_manager: DataManager, current_day_index: int) -> float:
        """Parser for parsing the key into the indicator value."""
        key_number_groupings = self.find_all_nums_in_str(rule_key)

        # MACD can only have slope emblem therefore 1 or 0 number groupings are acceptable
        if len(key_number_groupings) == 0:
            if SLOPE_SYMBOL in rule_key:
                raise StrategyIndicatorError(f'{self.strategy_symbol} rule key: {rule_key} does not contain'
                                             f' enough number groupings!')
            indicator_value = float(data_manager.get_data_point(self.DATA_COLUMN_TITLE, current_day_index))
        elif len(key_number_groupings) == 1:
            # 1 number grouping suggests the $slope indicator is being used
            if SLOPE_SYMBOL in rule_key:
                slope_window_length = int(key_number_groupings[0])

                # data request length is window - 1 to account for the current day index being a part of the window
                slope_data_request_length = slope_window_length - 1

                indicator_value = self.calculate_slope(
                    float(data_manager.get_data_point(self.DATA_COLUMN_TITLE, current_day_index)),
                    float(data_manager.get_data_point(self.DATA_COLUMN_TITLE, current_day_index -
                                                      slope_data_request_length)),
                    slope_window_length
                )
            else:
                raise StrategyIndicatorError(f'{self.strategy_symbol} rule key: {rule_key} contains too many number '
                                             f'groupings! Are you missing a $slope emblem?')
        else:
            raise StrategyIndicatorError(f'{self.strategy_symbol} rule key: {rule_key} contains '
                                         f'invalid number groupings!')

        return indicator_value

    def __calculate_macd(self, price_data: list) -> list:
        """Calculate MACD values for a list of price values"""
        large_ema_length_values = MACDTrigger.__calculate_ema(self.LARGE_EMA_LENGTH, price_data)

        small_ema_length_values = MACDTrigger.__calculate_ema(self.SMALL_EMA_LENGTH, price_data)

        if len(large_ema_length_values) != len(small_ema_length_values):
            raise StrategyIndicatorError(f'{self.strategy_symbol} value lists for {self.strategy_symbol} must be the '
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

    @staticmethod
    def __calculate_ema(length: int, price_data: list) -> list:
        """Calculates the EMA values for a list of price values."""
        k = 2 / (length + 1)

        previous_ema = MACDTrigger.__calculate_sma(length, price_data[0:length])[-1]

        ema_values = []
        for i in range(len(price_data)):
            if i < length:
                ema_values.append(None)
            else:
                ema = round((k * (float(price_data[i]) - previous_ema)) + previous_ema, 3)
                ema_values.append(ema)
                previous_ema = ema
        return ema_values

    @staticmethod
    def __calculate_sma(length: int, price_data: list) -> list:
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
