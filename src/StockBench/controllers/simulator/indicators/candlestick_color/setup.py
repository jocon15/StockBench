from typing import Union

from StockBench.controllers.simulator.indicator.exceptions import StrategyIndicatorError
from StockBench.controllers.simulator.indicator.setup_interface import SetupInterface
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager


class CandleStickSetup(SetupInterface):
    def __init__(self, strategy_symbol: str):
        super().__init__(strategy_symbol)

    def calculate_additional_days_from_rule_key(self, rule_key: str, rule_value: Union[str, int, dict, None]) -> int:
        # Candlestick is a unique indicator
        #   color: {
        #       "0", "red",
        #       "1", "green"
        #       }
        #   Key = color
        #   Value = {...}
        # You cannot deduce the length from the key, and you cannot identify the indicator from the value.
        # Therefore, we must have rule_value as a parameter to this function because rule_key identifies this as a color
        # trigger, and rule_value shows us the length.

        if len(rule_value.keys()) == 0:
            raise StrategyIndicatorError(f'Color rules must have at least one color child!')

        additional_days = 0
        for sub_key in rule_value.keys():
            if int(sub_key) > additional_days:
                additional_days = int(sub_key)
        return additional_days

    def calculate_additional_days_from_rule_value(self, rule_value: Union[str, int, dict]) -> int:
        # cannot deduce additional days from color rule value
        return 0

    def add_indicator_data_from_rule_key(self, rule_key: str, rule_value: Union[str, int, dict], side: str,
                                         data_manager: DataManager):
        # candle colors are included in the data by default
        return

    def add_indicator_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        # candle colors are included in the data by default
        return
