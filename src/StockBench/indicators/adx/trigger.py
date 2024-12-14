import logging
import statistics
from StockBench.constants import *
from StockBench.indicator.trigger import Trigger
from StockBench.indicator.exceptions import StrategyIndicatorError
from StockBench.simulation_data.data_manager import DataManager

log = logging.getLogger()


class ADXTrigger(Trigger):
    def __init__(self, strategy_symbol: str):
        super().__init__(strategy_symbol, side=Trigger.AGNOSTIC)

    def additional_days(self, rule_key: str, value_value: any) -> int:
        """Calculate the additional days required.

        Args:
            rule_key (any): The key value from the strategy.
            value_value (any): The value from the strategy.
        """
        rule_key_number_groups = self.find_all_nums_in_str(rule_key)
        if len(rule_key_number_groups) > 0:
            return max(list(map(int, rule_key_number_groups)))
        else:
            return DEFAULT_ADX_LENGTH


    def __add_adx_column(self, length: int, data_manager: DataManager):
        """Calculate the ADX values and add them to the df."""
        # if we already have RSI upper values in the df, we don't need to add them again
        for col_name in data_manager.get_column_names():
            if self.strategy_symbol in col_name:
                return

        # FIXME: this needs to fetch all O H L C values
        price_data = data_manager.get_column_data(data_manager.CLOSE)

        adx_values = self.

    @staticmethod
    def __calculate_adx(length: int, price_data: list):
        """Calculate the ADX values for a list of price values."""
        # FIXME, this needs to accepts O H L C lists

        # https://www.youtube.com/watch?v=LKDJQLrXedg - ADX step by step