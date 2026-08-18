import logging

from typing import Union

from StockBench.controllers.simulator.indicator.rule_interface import RuleInterface
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager
from StockBench.models.position.position import Position

log = logging.getLogger()


class VolumeRule(RuleInterface):
    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=RuleInterface.AGNOSTIC)

    def get_indicator_value_when_referenced(self, rule_value: str, data_manager: DataManager,
                                            current_day_index: int) -> float:
        raise NotImplementedError('Volume cannot be referenced in a rule value')

    def check_triggered(self, rule_key: str, rule_value: Union[str, int, dict], data_manager: DataManager,
                        position: Position, current_day_index: int) -> bool:
        volume = data_manager.get_data_point(data_manager.VOLUME, current_day_index)

        result = self.basic_trigger_check(float(volume), str(rule_value))

        log.debug(f'{self.indicator_symbol} algorithm: {rule_key} checked successfully')

        return result
