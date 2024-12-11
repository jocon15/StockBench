import logging
from StockBench.constants import *
from StockBench.indicator.trigger import Trigger
from StockBench.indicator.exceptions import StrategyIndicatorError
from StockBench.simulation_data.data_manager import DataManager
from StockBench.position.position import Position

log = logging.getLogger()


class StochasticTrigger(Trigger):
    # cannot use strategy symbol because it is "stochastic"
    DISPLAY_NAME = 'Stochastic'

    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol, side=Trigger.AGNOSTIC)

    def additional_days(self, rule_key, value_value) -> int:
        """Calculate the additional days required.

        Args:
            rule_key (any): The key value from the strategy.
            value_value (any): The value from the strategy.
        """
        # map to a list of ints
        rule_key_number_groups = list(map(int, self.find_all_nums_in_str(rule_key)))
        if rule_key_number_groups:
            return max(rule_key_number_groups)
        return DEFAULT_STOCHASTIC_LENGTH

    def add_to_data(self, rule_key, rule_value, side, data_manager):
        """Add data to the dataframe.

        Args:
            rule_key (any): The key value from the strategy.
            rule_value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (DataManager): The data object.
        """
        # ======== key based =========
        rule_key_number_groups = self.find_all_nums_in_str(rule_key)
        if len(rule_key_number_groups) > 0:
            num = int(rule_key_number_groups[0])
            self.__add_stochastic_column(num, data_manager)
        else:
            self.__add_stochastic_column(DEFAULT_STOCHASTIC_LENGTH, data_manager)
        # ======== value based (stochastic limit)=========
        rule_key_number_groups = self.find_all_nums_in_str(rule_value)
        if len(rule_key_number_groups) > 0:
            trigger = float(rule_key_number_groups[0])
            self.__add_stochastic_trigger_column(trigger, data_manager)

    def check_trigger(self, rule_key, rule_value, data_manager, position, current_day_index) -> bool:
        """Trigger logic for stochastic.

        Args:
            rule_key (str): The key value of the algorithm.
            rule_value (str): The value of the algorithm.
            data_manager (DataManager): The data API object.
            position (Position): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if a trigger was hit.
        """
        log.debug(f'Checking stochastic algorithm: {rule_key}...')

        indicator_value = self.__parse_key(rule_key, data_manager, current_day_index)

        operator, trigger_value = self._parse_rule_value(rule_value, data_manager, current_day_index)

        log.debug(f'{self.DISPLAY_NAME} algorithm: {rule_key} checked successfully')

        return Trigger.basic_trigger_check(indicator_value, operator, trigger_value)

    def __parse_key(self, rule_key, data_manager, current_day_index) -> float:
        """Parser for parsing the key into the indicator value."""
        # find the indicator value (left hand side of the comparison)
        rule_key_number_groups = self.find_all_nums_in_str(rule_key)

        if len(rule_key_number_groups) == 0:
            if SLOPE_SYMBOL in rule_key:
                raise StrategyIndicatorError(f'{self.DISPLAY_NAME} rule key: {rule_key} does not contain enough number '
                                             f'groupings!')
            indicator_value = float(data_manager.get_data_point(self.strategy_symbol, current_day_index))
        elif len(rule_key_number_groups) == 1:
            if SLOPE_SYMBOL in rule_key:
                # make sure the number is after the slope emblem and not the stochastic emblem
                if rule_key.split(str(rule_key_number_groups))[0] == self.strategy_symbol + SLOPE_SYMBOL:
                    raise StrategyIndicatorError(
                        f'{self.DISPLAY_NAME} rule key: {rule_key} contains too many number groupings! '
                        f'Are you missing a $slope emblem?')
            indicator_value = float(data_manager.get_data_point(self.strategy_symbol, current_day_index))
        elif len(rule_key_number_groups) == 2:
            title = f'{self.strategy_symbol}{int(rule_key_number_groups[0])}'
            # 2 number groups suggests $slope indicator is being used
            if SLOPE_SYMBOL in rule_key:
                slope_window_length = int(rule_key_number_groups[1])

                # data request length is window - 1 to account for the current day index being a part of the window
                slope_data_request_length = slope_window_length - 1

                indicator_value = self.calculate_slope(
                    float(data_manager.get_data_point(title, current_day_index)),
                    float(data_manager.get_data_point(title, current_day_index - slope_data_request_length)),
                    slope_window_length
                )
            else:
                raise StrategyIndicatorError(f'{self.DISPLAY_NAME} rule key: {rule_key} contains '
                                             f'too many number groupings! Are you missing a $slope emblem?')
        else:
            raise StrategyIndicatorError(f'{self.DISPLAY_NAME} rule key: {rule_key} contains '
                                         f'too many number groupings!')

        return indicator_value

    def __add_stochastic_column(self, length: int, data_manager: DataManager):
        """Calculate the stochastic values and add them to the df."""
        # if we already have values in the df, we don't need to add them again
        for col_name in data_manager.get_column_names():
            if self.strategy_symbol in col_name:
                return

        high_data = data_manager.get_column_data(data_manager.HIGH)
        low_data = data_manager.get_column_data(data_manager.LOW)
        close_data = data_manager.get_column_data(data_manager.CLOSE)

        stochastic_values = StochasticTrigger.__stochastic_oscillator(length, high_data, low_data, close_data)

        data_manager.add_column(self.strategy_symbol, stochastic_values)

    def __add_stochastic_trigger_column(self, trigger_value: float, data_manager: DataManager):
        """Add upper RSI algorithm to the df.

        In a stochastic chart, the stochastic triggers are mapped as horizontal bars on top of the stochastic chart.
        To ensure that these horizontal bars get mapped onto the chart, they must be added to the data as a column of
        static values that match the trigger value.
        """
        trigger_column_name = f'{self.strategy_symbol}_{trigger_value}'

        # if we already have a stochastic trigger column with this value in the df, we don't need to add it again
        for col_name in data_manager.get_column_names():
            if trigger_column_name == col_name:
                return

        list_values = [trigger_value for _ in range(data_manager.get_data_length())]

        data_manager.add_column(trigger_column_name, list_values)

    @staticmethod
    def __stochastic_oscillator(length: int, high_data: list, low_data: list, close_data: list) -> list:
        """Calculate the stochastic values for a list of price values."""
        past_length_days_high = []
        past_length_days_low = []
        past_length_days_close = []
        stochastic_oscillator = []
        for i in range(len(close_data)):
            if i < length:
                past_length_days_high.append(float(high_data[i]))
                past_length_days_low.append(float(low_data[i]))
                past_length_days_close.append(float(close_data[i]))
            else:
                past_length_days_high.pop(0)
                past_length_days_low.pop(0)
                past_length_days_close.pop(0)
                past_length_days_high.append(float(high_data[i]))
                past_length_days_low.append(float(low_data[i]))
                past_length_days_close.append(float(close_data[i]))

            stochastic_oscillator.append(round(((float(close_data[i]) - min(past_length_days_low)) /
                                                (max(past_length_days_high) - min(past_length_days_low))) * 100.0, 3))

        return stochastic_oscillator
