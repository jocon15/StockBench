import logging
from StockBench.indicator.trigger import Trigger
from StockBench.simulation_data.data_manager import DataManager

log = logging.getLogger()


class PriceTrigger(Trigger):
    # cannot use strategy symbol because its "price"
    DISPLAY_NAME = 'Price'

    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=Trigger.AGNOSTIC)

    def additional_days_from_rule_key(self, rule_key, rule_value) -> int:
        """Calculate the additional days required from rule key.

        Args:
            rule_key (any): The key value from the strategy.
            rule_value (any): The key value from the strategy (unused in this function).
        """
        # price does not require any additional days
        return 0

    def additional_days_from_rule_value(self, rule_value: any) -> int:
        """Calculate the additional days required from rule value."""
        # price does not require any additional days
        return 0

    def add_to_data_from_rule_key(self, rule_key, rule_value, side, data_manager):
        """Add data to the dataframe.

        Args:
            rule_key (any): The key value from the strategy.
            rule_value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (any): The data object.
        """
        # price is in the data by default, no need to add it
        return

    def add_to_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        """Add data to the dataframe from rule value."""
        # price is in the data by default, no need to add it
        return

    def get_value_when_referenced(self, rule_value: str, data_manager: DataManager, current_day_index) -> float:
        """Get the value of the indicator when referenced in a rule value."""
        # parse rule key will work even when passed a rule value
        return Trigger._parse_rule_key_no_indicator_length(rule_value, self.indicator_symbol, data_manager,
                                                           current_day_index, data_manager.CLOSE)

    def check_trigger(self, rule_key, rule_value, data_manager, position, current_day_index) -> bool:
        """Trigger logic for price.

        Args:
            rule_key (str): The key value of the algorithm.
            rule_value (str): The value of the algorithm.
            data_manager (any): The data API object.
            position (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if a trigger was hit.
        """
        log.debug(f'Checking price algorithm: {rule_key}...')

        # price uses special key parses because the indicator called 'price', but in the data it is 'close', to make it
        # more clear we are using a dedicate parser
        indicator_value = Trigger._parse_rule_key_no_indicator_length(rule_key, self.indicator_symbol, data_manager,
                                                                      current_day_index, data_manager.CLOSE)

        log.debug(f'Price algorithm: {rule_key} checked successfully')

        return self.basic_trigger_check(indicator_value, rule_value)
