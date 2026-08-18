import logging

from typing import Union

from StockBench.models.position.position import Position
from StockBench.controllers.simulator.indicator.trigger_interface import TriggerInterface
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager

log = logging.getLogger()


class PriceTrigger(TriggerInterface):
    # cannot use strategy symbol because its "price"
    DISPLAY_NAME = 'Price'

    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=TriggerInterface.AGNOSTIC)

    def get_indicator_value_when_referenced(self, rule_value: str, data_manager: DataManager,
                                            current_day_index: int) -> float:
        # parse rule key will work even when passed a rule value
        return TriggerInterface._parse_rule_key_no_indicator_length(rule_value, self.indicator_symbol, data_manager,
                                                                    current_day_index, data_manager.CLOSE)

    def check_trigger(self, rule_key: str, rule_value: Union[str, int, dict], data_manager: DataManager,
                      position: Position, current_day_index: int) -> bool:
        log.debug(f'Checking price algorithm: {rule_key}...')

        # price uses special key parses because the indicator called 'price', but in the data it is 'close', to make it
        # more clear we are using a dedicate parser
        indicator_value = TriggerInterface._parse_rule_key_no_indicator_length(rule_key, self.indicator_symbol,
                                                                               data_manager, current_day_index,
                                                                               data_manager.CLOSE)

        log.debug(f'Price algorithm: {rule_key} checked successfully')

        return self.basic_trigger_check(indicator_value, str(rule_value))
