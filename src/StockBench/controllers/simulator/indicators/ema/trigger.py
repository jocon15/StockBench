import logging

from StockBench.models.position.position import Position
from StockBench.controllers.simulator.indicator import Trigger
from StockBench.controllers.simulator.indicator import StrategyIndicatorError
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager
from StockBench.indicators.sma.sma import SMATrigger

log = logging.getLogger()


class EMATrigger(Trigger):
    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=Trigger.AGNOSTIC)

    def calculate_additional_days_from_rule_key(self, rule_key: str, rule_value: any) -> int:
        rule_key_number_groups = list(map(int, self.find_all_nums_in_str(rule_key)))
        if rule_key_number_groups:
            return max(rule_key_number_groups)
        raise StrategyIndicatorError(f'{self.indicator_symbol} indicator must have an indicator length!')

    def calculate_additional_days_from_rule_value(self, rule_value: any) -> int:
        # logic for rule value is the same as the logic for rule key
        return self.calculate_additional_days_from_rule_key(rule_value, None)

    def add_indicator_data_from_rule_key(self, rule_key: str, rule_value: any, side: str, data_manager: DataManager):
        nums = self.find_all_nums_in_str(rule_key)
        if len(nums) > 0:
            indicator_length = int(nums[0])
            self.__add_ema_to_simulation_data(indicator_length, data_manager)
        else:
            raise StrategyIndicatorError(f'{self.indicator_symbol} key: {rule_key} must have an indicator length!')

    def add_indicator_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        # logic for rule value is the same as the logic for rule key
        return self.add_indicator_data_from_rule_key(rule_value, None, side, data_manager)

    def get_indicator_value_when_referenced(self, rule_value: str, data_manager: DataManager,
                                            current_day_index: int) -> float:
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

    def __add_ema_to_simulation_data(self, length: int, data_manager: DataManager):
        """Adds EMA indicator data to the simulation data."""
        column_title = f'{self.indicator_symbol}{length}'

        # skip if there are EMA values in the simulation data
        for col_name in data_manager.get_column_names():
            if column_title in col_name:
                return

        price_data = data_manager.get_column_data(data_manager.CLOSE)
        ema_values = EMATrigger.calculate_ema(length, price_data)

        data_manager.add_column(column_title, ema_values)

    @staticmethod
    def calculate_ema(length: int, price_data: list) -> list:
        """Calculates the EMA values for a list of price values."""
        k = 2 / (length + 1)

        # get the initial ema value (uses sma of length days)
        previous_ema = SMATrigger.calculate_sma(length, price_data[0:length])[-1]

        ema_values = []
        for i in range(len(price_data)):
            if i < length:
                ema_values.append(None)
            else:
                ema_point = round((k * (float(price_data[i]) - previous_ema)) + previous_ema, 3)
                ema_values.append(ema_point)
                previous_ema = ema_point
        return ema_values
