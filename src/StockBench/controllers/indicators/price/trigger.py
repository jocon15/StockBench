import logging

from StockBench.position.position import Position
from StockBench.controllers.indicator import Trigger
from StockBench.controllers.simulation_data.data_manager import DataManager

log = logging.getLogger()


class PriceTrigger(Trigger):
    # cannot use strategy symbol because its "price"
    DISPLAY_NAME = 'Price'

    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=Trigger.AGNOSTIC)

    def calculate_additional_days_from_rule_key(self, rule_key: str, rule_value: any) -> int:
        return 0

    def calculate_additional_days_from_rule_value(self, rule_value: any) -> int:
        return 0

    def add_indicator_data_from_rule_key(self, rule_key: str, rule_value: any, side: str, data_manager: DataManager):
        # price is in the data by default, no need to add it
        return

    def add_indicator_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        # price is in the data by default, no need to add it
        return

    def get_indicator_value_when_referenced(self, rule_value: str, data_manager: DataManager,
                                            current_day_index: int) -> float:
        # parse rule key will work even when passed a rule value
        return Trigger._parse_rule_key_no_indicator_length(rule_value, self.indicator_symbol, data_manager,
                                                           current_day_index, data_manager.CLOSE)

    def check_trigger(self, rule_key: str, rule_value: any, data_manager: DataManager, position: Position,
                      current_day_index: int) -> bool:
        log.debug(f'Checking price algorithm: {rule_key}...')

        # price uses special key parses because the indicator called 'price', but in the data it is 'close', to make it
        # more clear we are using a dedicate parser
        indicator_value = Trigger._parse_rule_key_no_indicator_length(rule_key, self.indicator_symbol, data_manager,
                                                                      current_day_index, data_manager.CLOSE)

        log.debug(f'Price algorithm: {rule_key} checked successfully')

        return self.basic_trigger_check(indicator_value, rule_value)
