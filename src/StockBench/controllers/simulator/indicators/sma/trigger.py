import logging
import statistics

from StockBench.controllers.simulator.indicator import Trigger
from StockBench.controllers.simulator.indicator import StrategyIndicatorError
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager
from StockBench.models.position.position import Position

log = logging.getLogger()


class SMATrigger(Trigger):
    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=Trigger.AGNOSTIC)

    def calculate_additional_days_from_rule_key(self, rule_key: str, rule_value: any) -> int:
        rule_key_number_groups = list(map(int, self.find_all_nums_in_str(rule_key)))
        if rule_key_number_groups:
            return max(rule_key_number_groups)
        raise StrategyIndicatorError(f'{self.indicator_symbol} rule key: {rule_key} must have an indicator length!')

    def calculate_additional_days_from_rule_value(self, rule_value: any) -> int:
        # logic for rule value is the same as the logic for rule key
        return self.calculate_additional_days_from_rule_key(rule_value, None)

    def add_indicator_data_from_rule_key(self, rule_key: str, rule_value: any, side: str, data_manager: DataManager):
        rule_key_number_groups = self.find_all_nums_in_str(rule_key)
        if len(rule_key_number_groups) > 0:
            indicator_length = int(rule_key_number_groups[0])
            self.__add_sma_to_simulation_data(indicator_length, data_manager)
        else:
            raise StrategyIndicatorError(f'{self.indicator_symbol} rule key: {rule_key} must have an indicator length!')

    def add_indicator_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        # logic for rule value is the same as the logic for rule key
        return self.add_indicator_data_from_rule_key(rule_value, None, side, data_manager)

    def get_indicator_value_when_referenced(self, rule_value: str, data_manager: DataManager,
                                            current_day_index) -> float:
        # parse rule key will work even when passed a rule value
        return Trigger._parse_rule_key_no_default_indicator_length(rule_value, self.indicator_symbol, data_manager,
                                                                   current_day_index)

    def check_trigger(self, rule_key: str, rule_value: any, data_manager: DataManager, position: Position,
                      current_day_index: int) -> bool:
        log.debug(f'Checking {self.indicator_symbol} algorithm: {rule_key}...')

        indicator_value = Trigger._parse_rule_key_no_default_indicator_length(rule_key, self.indicator_symbol,
                                                                              data_manager, current_day_index)

        log.debug(f'{self.indicator_symbol} algorithm: {rule_key} checked successfully')

        return self.basic_trigger_check(indicator_value, rule_value)

    def __add_sma_to_simulation_data(self, length: int, data_manager: DataManager):
        """Adds SMA indicator values to the simulation data."""
        column_title = f'{self.indicator_symbol}{length}'

        # if SMA values ar already in the df, we don't need to add them again
        for col_name in data_manager.get_column_names():
            if column_title in col_name:
                return

        price_data = data_manager.get_column_data(data_manager.CLOSE)
        sma_values = SMATrigger.calculate_sma(length, price_data)

        data_manager.add_column(column_title, sma_values)

    @staticmethod
    def calculate_sma(length: int, price_data: list) -> list:
        """Calculates the SMA values for a list of price values."""
        price_values = []
        sma_values = []
        all_sma_values = []
        for element in price_data:
            if len(price_values) < length:
                price_values.append(float(element))
            else:
                price_values.pop(0)
                sma_values.pop(0)
                price_values.append(float(element))
            avg = round(statistics.mean(price_values), 3)
            sma_values.append(avg)
            all_sma_values.append(avg)
        return all_sma_values
