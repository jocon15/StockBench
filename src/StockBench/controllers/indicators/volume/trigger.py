import logging

from StockBench.controllers.indicator import Trigger
from StockBench.controllers.simulation_data.data_manager import DataManager
from StockBench.position.position import Position

log = logging.getLogger()


class VolumeTrigger(Trigger):
    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=Trigger.AGNOSTIC)

    def calculate_additional_days_from_rule_key(self, rule_key: str, rule_value: any) -> int:
        return 0

    def calculate_additional_days_from_rule_value(self, rule_value: any) -> int:
        return 0

    def add_indicator_data_from_rule_key(self, rule_key: str, rule_value: any, side: str, data_manager: DataManager):
        # volume does not require any additional data to be added to the data
        return

    def add_indicator_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        # volume does not require any additional data to be added to the data
        return

    def get_indicator_value_when_referenced(self, rule_value: str, data_manager: DataManager,
                                            current_day_index: int) -> float:
        raise NotImplementedError('Volume cannot be referenced in a rule value')

    def check_trigger(self, rule_key: str, rule_value: any, data_manager: DataManager, position: Position,
                      current_day_index: int) -> bool:
        volume = data_manager.get_data_point(data_manager.VOLUME, current_day_index)

        result = self.basic_trigger_check(volume, rule_value)

        log.debug(f'{self.indicator_symbol} algorithm: {rule_key} checked successfully')

        return result
