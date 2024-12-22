import logging
import statistics
from StockBench.indicator.trigger import Trigger
from StockBench.indicator.exceptions import StrategyIndicatorError
from StockBench.simulation_data.data_manager import DataManager
from StockBench.indicators.sma.sma import SMATrigger

log = logging.getLogger()


class EMATrigger(Trigger):
    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=Trigger.AGNOSTIC)

    def additional_days(self, rule_key, value_value) -> int:
        """Calculate the additional days required.

        Args:
            rule_key (any): The key value from the strategy.
            value_value (any): The value from the strategy.
        """
        # map to a list of ints
        nums = list(map(int, self.find_all_nums_in_str(rule_key)))
        if nums:
            return max(nums)
        raise StrategyIndicatorError(f'{self.indicator_symbol} key: {rule_key} must have an indicator length!')

    def add_to_data(self, rule_key, rule_value, side, data_manager):
        """Add data to the dataframe.

        Args:
            rule_key (any): The key value from the strategy.
            rule_value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (DataManager): The data object.
        """
        nums = self.find_all_nums_in_str(rule_key)
        if len(nums) > 0:
            indicator_length = int(nums[0])
            self.__add_ema(indicator_length, data_manager)
        else:
            raise StrategyIndicatorError(f'{self.indicator_symbol} key: {rule_key} must have an indicator length!')

    def check_trigger(self, rule_key, rule_value, data_manager, position, current_day_index) -> bool:
        """Trigger logic for EMA.

        Args:
            rule_key (any): The key value of the algorithm.
            rule_value (any): The value of the algorithm.
            data_manager (DataManager): The data API object.
            position (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if a trigger was hit.
        """
        log.debug(f'Checking {self.indicator_symbol} algorithm: {rule_key}...')

        indicator_value = Trigger._parse_rule_key_no_default_indicator_length(rule_key, self.indicator_symbol, data_manager,
                                                                              current_day_index)

        operator, trigger_value = self._parse_rule_value(rule_value, data_manager, current_day_index)

        log.debug(f'{self.indicator_symbol} algorithm: {rule_key} checked successfully')

        return Trigger.basic_trigger_check(indicator_value, operator, trigger_value)

    def __add_ema(self, length: int, data_manager: DataManager):
        """Pre-calculate the EMA values and add them to the df."""
        column_title = f'{self.indicator_symbol}{length}'

        # if we already have EMA values in the df, we don't need to add them again
        for col_name in data_manager.get_column_names():
            if column_title in col_name:
                return

        price_data = data_manager.get_column_data(data_manager.CLOSE)

        ema_values = EMATrigger.calculate_ema(length, price_data)

        data_manager.add_column(column_title, ema_values)

    @staticmethod
    def calculate_ema(length: int, price_data: list) -> list:
        """Calculates the EMA values for a list of price values"""
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
