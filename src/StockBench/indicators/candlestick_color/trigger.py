import logging
from StockBench.indicator.trigger import Trigger
from StockBench.indicator.exceptions import StrategyIndicatorError

log = logging.getLogger()


class CandlestickColorTrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol, side=Trigger.AGNOSTIC)

    def additional_days(self, rule_key, value_value) -> int:
        """Calculate the additional days required.

        Args:
            rule_key (any): The key value from the strategy (unused in this function).
            value_value (any): The value from the strategy.
        """
        if len(value_value.keys()) == 0:
            raise StrategyIndicatorError(f'{self.strategy_symbol} key: {rule_key} must have at least one color child key')

        additional_days = 0
        for sub_key in value_value.keys():
            if int(sub_key) > additional_days:
                additional_days = int(sub_key)
        return additional_days

    def add_to_data(self, rule_key, rule_value, side, data_manager):
        """Add data to the dataframe.

        Args:
            rule_key (any): The key value from the strategy.
            rule_value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (any): The data object.
        """
        # candle colors are included by default
        return

    def check_trigger(self, rule_key, rule_value, data_manager, position, current_day_index) -> bool:
        """Trigger logic for candlestick color.

        Args:
            rule_key (str): The key value of the algorithm.
            rule_value (dict): The value of the algorithm.
            data_manager (any): The data API object.
            position (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the algorithm was hit.
        """
        log.debug('Checking candle stick algorithm...')

        # find out how many keys there are (value is a dict)
        num_keys = len(rule_value)

        if num_keys == 0:
            raise StrategyIndicatorError(f'{self.strategy_symbol} key: {rule_key} must have at least one color child key')

        # these will both need to be in ascending order [today, yesterday...]
        trigger_colors = []
        actual_colors = []

        # build the algorithm list
        for value_key in sorted(rule_value.keys()):
            trigger_colors.append(rule_value[value_key])

        # build the actual list
        for i in range(num_keys):
            actual_colors.append(data_manager.get_data_point(data_manager.COLOR, current_day_index-i))

        # check for algorithm
        if actual_colors == trigger_colors:
            log.info('Candle stick algorithm hit!')
            return True

        log.debug('All candle stick algorithm checked')

        # catch all case if nothing was hit (which is ok!)
        return False
