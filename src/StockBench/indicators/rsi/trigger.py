import logging
import statistics

from StockBench.constants import *
from StockBench.indicator.trigger import Trigger
from StockBench.simulation_data.data_manager import DataManager
from StockBench.position.position import Position

log = logging.getLogger()


class RSITrigger(Trigger):
    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=Trigger.AGNOSTIC)

    def calculate_additional_days_from_rule_key(self, rule_key: str, rule_value: any) -> int:
        rule_key_number_groups = self.find_all_nums_in_str(rule_key)
        if len(rule_key_number_groups) > 0:
            return max(list(map(int, rule_key_number_groups)))
        else:
            return DEFAULT_RSI_LENGTH

    def calculate_additional_days_from_rule_value(self, rule_value: any) -> int:
        # logic for rule value is the same as the logic for rule key
        return self.calculate_additional_days_from_rule_key(rule_value, None)

    def add_indicator_data_from_rule_key(self, rule_key: str, rule_value: any, side: str, data_manager: DataManager):
        # ======== key based =========
        # (adds the RSI values to the data based on the key)
        nums = self.find_all_nums_in_str(rule_key)
        if len(nums) > 0:
            num = int(nums[0])
            self.__add_rsi_to_simulation_data(num, data_manager)
        else:
            self.__add_rsi_to_simulation_data(DEFAULT_RSI_LENGTH, data_manager)
        # ======== value based (rsi limit)=========
        # (adds the RSI limit values to the data for charting)
        nums = self.find_all_nums_in_str(rule_value)
        if len(nums) > 0:
            trigger_value = float(nums[0])
            Trigger._add_trigger_value_as_column(f'{self.indicator_symbol}_{trigger_value}', trigger_value,
                                                 data_manager)

    def add_indicator_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        rule_value_number_groups = self.find_all_nums_in_str(rule_value)
        if len(rule_value_number_groups) > 0:
            num = int(rule_value_number_groups[0])
            self.__add_rsi_to_simulation_data(num, data_manager)
        else:
            self.__add_rsi_to_simulation_data(DEFAULT_RSI_LENGTH, data_manager)

    def get_indicator_value_when_referenced(self, rule_value: str, data_manager: DataManager,
                                            current_day_index: int) -> float:
        # parse rule key will work even when passed a rule value
        return Trigger._parse_rule_key(rule_value, self.indicator_symbol, data_manager, current_day_index)

    def check_trigger(self, rule_key: str, rule_value: any, data_manager: DataManager, position: Position,
                      current_day_index: int) -> bool:
        log.debug(f'Checking {self.indicator_symbol} algorithm: {rule_key}...')

        indicator_value = Trigger._parse_rule_key(rule_key, self.indicator_symbol, data_manager, current_day_index)

        log.debug(f'{self.indicator_symbol} algorithm: {rule_key} checked successfully')

        return self.basic_trigger_check(indicator_value, rule_value)

    def __add_rsi_to_simulation_data(self, length: int, data_manager: DataManager):
        """Adds RSI indicator data to the simulation data."""
        # if we already have RSI upper values in the df, we don't need to add them again
        for col_name in data_manager.get_column_names():
            if self.indicator_symbol in col_name:
                return

        price_data = data_manager.get_column_data(data_manager.CLOSE)

        rsi_values = RSITrigger.calculate_rsi(length, price_data)

        data_manager.add_column(self.indicator_symbol, rsi_values)

    @staticmethod
    def calculate_rsi(length: int, price_data: list) -> list:
        """Calculates the RSI values for a list of price values."""
        first_day_value = 0
        gain = []
        loss = []
        rsi = []
        all_rsi = []  # archive to return
        for i in range(1, len(price_data)):
            dif = float(price_data[i]) - float(price_data[i - 1])
            if dif > 0:
                if len(gain) == length:
                    gain.pop(0)
                    gain.append(dif)
                else:
                    gain.append(dif)
            elif dif < 0:
                if len(loss) == length:
                    loss.pop(0)
                    loss.append(abs(dif))
                else:
                    loss.append(abs(dif))
            if len(gain) > 0 and len(loss) > 0:
                avg_gain = statistics.mean(gain)
                avg_loss = statistics.mean(loss)
                rs = avg_gain / avg_loss
                rs_index = round(100 - (100 / (1 + rs)), 3)
                if len(rsi) == 6:
                    rsi.pop(0)
                    rsi.append(rs_index)
                else:
                    rsi.append(rs_index)
                if i == 1:
                    first_day_value = rs_index
                all_rsi.append(rs_index)

        # ensure that the data returned is the same size
        # **
        # Note: Given that the simulation has additional days,
        # the days that these values are assigned to will not be seen
        # by the simulation
        # **
        if len(all_rsi) != len(price_data):
            dif = len(price_data) - len(all_rsi)
            for _ in range(dif):
                # append initial values to the front of the list
                all_rsi.insert(0, first_day_value)

        return all_rsi
