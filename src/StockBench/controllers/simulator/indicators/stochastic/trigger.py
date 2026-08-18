import logging

from typing import Union

from StockBench.controllers.simulator.indicator.trigger_interface import TriggerInterface
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager
from StockBench.models.position.position import Position

log = logging.getLogger()


class StochasticTrigger(TriggerInterface):
    # cannot use strategy symbol because it is "stochastic"
    DISPLAY_NAME = 'Stochastic'

    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=TriggerInterface.AGNOSTIC)

    def get_indicator_value_when_referenced(self, rule_value: str, data_manager: DataManager,
                                            current_day_index: int) -> float:
        # parse rule key will work even when passed a rule value
        return TriggerInterface.parse_rule_key(rule_value, self.indicator_symbol, data_manager, current_day_index)

    def check_trigger(self, rule_key: str, rule_value: Union[str, int, dict], data_manager: DataManager,
                      position: Position, current_day_index: int) -> bool:
        log.debug(f'Checking stochastic algorithm: {rule_key}...')

        indicator_value = TriggerInterface.parse_rule_key(rule_key, self.indicator_symbol, data_manager,
                                                          current_day_index)

        log.debug(f'{self.DISPLAY_NAME} algorithm: {rule_key} checked successfully')

        return self.basic_trigger_check(indicator_value, str(rule_value))
