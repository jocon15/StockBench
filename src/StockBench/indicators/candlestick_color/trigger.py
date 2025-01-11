import logging
from StockBench.indicator.trigger import Trigger
from StockBench.indicator.exceptions import StrategyIndicatorError
from StockBench.simulation_data.data_manager import DataManager
from StockBench.position.position import Position

log = logging.getLogger()


class CandlestickColorTrigger(Trigger):
    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=Trigger.AGNOSTIC)

    def additional_days_from_rule_key(self, rule_key) -> int:
        """Calculate the additional days required from rule key.

        Args:
            rule_key (any): The key value from the strategy (unused in this function).
        """
        # cannot deduce additional days from color rule key
        return 0

    def additional_days_from_rule_value(self, rule_value: any) -> int:
        """Calculate the additional days required from rule value."""
        if len(rule_value.keys()) == 0:
            raise StrategyIndicatorError(f'Color rules must have at least one color child!')

        additional_days = 0
        for sub_key in rule_value.keys():
            if int(sub_key) > additional_days:
                additional_days = int(sub_key)
        return additional_days

    def add_to_data_from_rule_key(self, rule_key, rule_value, side, data_manager):
        """Add data to the dataframe.

        Args:
            rule_key (any): The key value from the strategy.
            rule_value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (DataManager): The data object.
        """
        # candle colors are included by default
        return

    def check_trigger(self, rule_key, rule_value, data_manager, position, current_day_index) -> bool:
        """Trigger logic for candlestick color.

        Args:
            rule_key (any): The key value of the algorithm.
            rule_value (any): The value of the algorithm.
            data_manager (DataManager): The data API object.
            position (Position): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if a trigger was hit.
        """
        log.debug('Checking candle stick algorithm...')

        key_count = len(rule_value)

        if key_count == 0:
            raise StrategyIndicatorError(f'{self.indicator_symbol} key: {rule_key} must have at least one color child '
                                         f'key')

        trigger_colors = [rule_value[value_key] for value_key in sorted(rule_value.keys())]
        actual_colors = [data_manager.get_data_point(data_manager.COLOR, current_day_index-i) for i in range(key_count)]

        if actual_colors == trigger_colors:
            log.info('Candle stick algorithm hit!')
            return True

        log.debug('All candle stick algorithm checked')

        # catch all case if nothing was hit (which is ok!)
        return False
