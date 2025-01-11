import logging
from StockBench.indicator.trigger import Trigger
from StockBench.simulation_data.data_manager import DataManager
from StockBench.position.position import Position

log = logging.getLogger()


class VolumeTrigger(Trigger):
    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=Trigger.AGNOSTIC)

    def additional_days_from_rule_key(self, rule_key, rule_value) -> int:
        """Calculate the additional days required from rule key.

        Args:
            rule_key (any): The key value from the strategy.
            rule_value (any): The key value from the strategy (unused in this function).
        """
        # volume does not require additional days
        return 0

    def additional_days_from_rule_value(self, rule_value: any) -> int:
        """Calculate the additional days required from rule value."""
        # volume does not require additional days
        return 0

    def add_to_data_from_rule_key(self, rule_key, rule_value, side, data_manager):
        """Add data to the dataframe from rule key.

        Args:
            rule_key (any): The key value from the strategy.
            rule_value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (any): The data object.
        """
        # volume does not require any additional data to be added to the data
        return

    def add_to_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        """Add data to the dataframe rule value."""
        # volume does not require any additional data to be added to the data
        return

    def get_value_when_referenced(self, rule_value: str, data_manager: DataManager, current_day_index,) -> float:
        raise NotImplementedError('Volume cannot be referenced in a rule value')

    def check_trigger(self, rule_key, rule_value, data_manager, position, current_day_index) -> bool:
        """Trigger logic for volume.

        Args:
            rule_key (any): The key value of the algorithm.
            rule_value (any): The value of the algorithm.
            data_manager (DataManager): The data API object.
            position (Position): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if a trigger was hit.
        """
        volume = data_manager.get_data_point(data_manager.VOLUME, current_day_index)

        result = self.basic_trigger_check(volume, rule_value, data_manager, current_day_index)

        log.debug(f'{self.indicator_symbol} algorithm: {rule_key} checked successfully')

        return result
