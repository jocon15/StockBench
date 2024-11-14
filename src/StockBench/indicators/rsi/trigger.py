import logging
import statistics
from StockBench.constants import *
from StockBench.indicator.trigger import Trigger
from StockBench.simulation_data.data_manager import DataManager
from StockBench.indicator.exceptions import StrategyIndicatorError

log = logging.getLogger()


class RSITrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol, side=Trigger.AGNOSTIC)

    def additional_days(self, rule_key, value_value) -> int:
        """Calculate the additional days required.

        Args:
            rule_key (any): The key value from the strategy.
            value_value (any): The value from the strategy.
        """
        nums = self.find_all_nums_in_str(rule_key)
        if len(nums) > 0:
            return max(list(map(int, nums)))
        else:
            return DEFAULT_RSI_LENGTH

    def add_to_data(self, rule_key, rule_value, side, data_manager):
        """Add data to the dataframe.

        Args:
            rule_key (any): The key value from the strategy.
            rule_value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (any): The data object.
        """
        # ======== key based =========
        # (adds the RSI values to the data based on the key)
        nums = self.find_all_nums_in_str(rule_key)
        if len(nums) > 0:
            num = int(nums[0])
            # add the RSI data to the df
            self.__add_rsi_column(num, data_manager)
        else:
            # add the RSI data to the df
            self.__add_rsi_column(DEFAULT_RSI_LENGTH, data_manager)
        # ======== value based (rsi limit)=========
        # (adds the RSI limit values to the data for charting)
        nums = self.find_all_nums_in_str(rule_value)
        # add the trigger to the df for charting
        if len(nums) > 0:
            trigger = float(nums[0])
            self.__add_rsi_trigger_column(trigger, data_manager)

    def check_trigger(self, rule_key, rule_value, data_manager, position, current_day_index) -> bool:
        """Trigger logic for RSI.

        Args:
            rule_key (str): The key value of the algorithm.
            rule_value (str): The value of the algorithm.
            data_manager (any): The data API object.
            position (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the algorithm was hit.
        """
        log.debug(f'Checking RSI algorithm: {rule_key}...')

        # get the indicator value from the key
        indicator_value = self.__parse_key(rule_key, data_manager, current_day_index)

        # get the operator and algorithm value from the value
        operator, trigger_value = self._parse_rule_value(rule_value, data_manager, current_day_index)

        log.debug(f'RSI algorithm: {rule_key} checked successfully')

        # algorithm checks
        return Trigger.basic_trigger_check(indicator_value, operator, trigger_value)

    def __parse_key(self, key, data_manager, current_day_index) -> float:
        """Parser for parsing the key into the indicator value."""
        # find the indicator value (left hand side of the comparison)
        nums = self.find_all_nums_in_str(key)

        if len(nums) == 0:
            # RSI is default length (14)
            if SLOPE_SYMBOL in key:
                raise StrategyIndicatorError(f'{self.strategy_symbol} key: {key} does not contain enough number '
                                             f'groupings!')
            indicator_value = float(data_manager.get_data_point(self.strategy_symbol, current_day_index))
        elif len(nums) == 1:
            if SLOPE_SYMBOL in key:
                # make sure the number is after the slope emblem and not the RSI emblem
                if key.split(str(nums))[0] == self.strategy_symbol + SLOPE_SYMBOL:
                    raise StrategyIndicatorError(f'{self.strategy_symbol} key: {key} does not contain a slope value!')
            # RSI is custom length (not 14)
            # title of the column in the data
            title = f'{self.strategy_symbol}{int(nums[0])}'
            indicator_value = float(data_manager.get_data_point(title, current_day_index))
        elif len(nums) == 2:
            # title of the column in the data
            title = f'RSI{int(nums[0])}'
            # likely that the $slope indicator is being used
            if SLOPE_SYMBOL in key:
                # get the length of the slope window
                slope_window_length = int(nums[1])

                # data request length is window - 1 to account for the current day index being a part of the window
                slope_data_request_length = slope_window_length - 1

                # calculate slope
                indicator_value = self.calculate_slope(
                    float(data_manager.get_data_point(title, current_day_index)),
                    float(data_manager.get_data_point(title, current_day_index - slope_data_request_length)),
                    slope_window_length
                )
            else:
                raise StrategyIndicatorError(f'{self.strategy_symbol} key: {key} contains too many number groupings! '
                                             f'Are you missing a $slope emblem?')
        else:
            raise StrategyIndicatorError(f'{self.strategy_symbol} key: {key} contains too many number groupings!')

        return indicator_value

    @staticmethod
    def __add_rsi_column(length, data_manager):
        """Calculate the RSI values and add them to the df.

        Args:
            length (int): The length of the RSI to use.
            data_manager (any): The data object.
        """
        # if we already have RSI upper values in the df, we don't need to add them again
        for col_name in data_manager.get_column_names():
            if 'RSI' in col_name:
                return

        # get a list of price values as a list
        price_data = data_manager.get_column_data(data_manager.CLOSE)

        # calculate the RSI values from the indicator API
        rsi_values = RSITrigger.__calculate_rsi(length, price_data)

        # add the calculated values to the df
        data_manager.add_column('RSI', rsi_values)

    @staticmethod
    def __add_rsi_trigger_column(trigger_value: float, data_manager: DataManager):
        """Add upper RSI algorithm to the df.

        In an RSI chart, the RSI triggers are mapped as horizontal bars on top of the RSI chart. To ensure that
        these horizontal bars get mapped onto the chart, they must be added to the data as a column of static values
        that match the trigger value.

        Args:
            trigger_value: The algorithm value for the upper RSI.
            data_manager: The data object.
        """
        trigger_column_name = f'RSI_{trigger_value}'

        # if we already have an RSI trigger column with this value in the df, we don't need to add it again
        for col_name in data_manager.get_column_names():
            if trigger_column_name == col_name:
                return

        # create a list of the algorithm value repeated
        list_values = [trigger_value for _ in range(data_manager.get_data_length())]

        # add the list to the data
        data_manager.add_column(trigger_column_name, list_values)

    @staticmethod
    def __calculate_rsi(length: int, price_data: list) -> list:
        """Calculate the RSI values for a list of price values.

        Args:
            length (int): The length of the RSI to calculate.
            price_data (list): The price data to calculate the RSI from.

        return:
            list: The list of calculated RSI values.
        """
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
