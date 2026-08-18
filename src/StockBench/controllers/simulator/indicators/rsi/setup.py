import statistics
from typing import Union

from StockBench.controllers.simulator.indicator.setup_interface import SetupInterface
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager
from StockBench.models.constants.general_constants import DEFAULT_RSI_LENGTH


class RSISetup(SetupInterface):
    def __init__(self, strategy_symbol: str):
        super().__init__(strategy_symbol)

    def calculate_additional_days_from_rule_key(self, rule_key: str, rule_value: Union[str, int, dict, None]) -> int:
        rule_key_number_groups = self.find_all_nums_in_str(rule_key)
        if len(rule_key_number_groups) > 0:
            return max(list(map(int, rule_key_number_groups)))
        else:
            return DEFAULT_RSI_LENGTH

    def calculate_additional_days_from_rule_value(self, rule_value: Union[str, int, dict]) -> int:
        # logic for rule value is the same as the logic for rule key
        return self.calculate_additional_days_from_rule_key(str(rule_value), None)

    def add_indicator_data_from_rule_key(self, rule_key: str, rule_value: Union[str, int, dict], side: str,
                                         data_manager: DataManager):
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
        nums = self.find_all_nums_in_str(str(rule_value))
        if len(nums) > 0:
            trigger_value = float(nums[0])
            self.add_trigger_value_as_column(f'{self.indicator_symbol}_{trigger_value}', trigger_value,
                                             data_manager)

    def add_indicator_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        rule_value_number_groups = self.find_all_nums_in_str(rule_value)
        if len(rule_value_number_groups) > 0:
            num = int(rule_value_number_groups[0])
            self.__add_rsi_to_simulation_data(num, data_manager)
        else:
            self.__add_rsi_to_simulation_data(DEFAULT_RSI_LENGTH, data_manager)

    def __add_rsi_to_simulation_data(self, length: int, data_manager: DataManager):
        """Adds RSI indicator data to the simulation data."""
        # if we already have RSI upper values in the df, we don't need to add them again
        for col_name in data_manager.get_column_names():
            if self.indicator_symbol in col_name:
                return

        price_data = data_manager.get_column_data(data_manager.CLOSE)

        rsi_values = RSISetup.calculate_rsi(length, price_data)

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
