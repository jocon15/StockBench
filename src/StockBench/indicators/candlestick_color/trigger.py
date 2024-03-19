import logging
from StockBench.indicator.trigger import Trigger

log = logging.getLogger()


class CandlestickColorTrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol, side=Trigger.AGNOSTIC)

    def additional_days(self, key, value) -> int:
        """Calculate the additional days required.

        Args:
            key (any): The key value from the strategy (unused in this function).
            value (any): The value from the strategy.
        """
        additional_days = 0
        for sub_key in value.keys():
            if int(sub_key) > additional_days:
                additional_days = int(sub_key)
        return additional_days

    def add_to_data(self, key, value, side, data_manager):
        """Add data to the dataframe.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (any): The data object.
        """
        # candle colors are included by default
        return

    def check_trigger(self, key, value, data_manager, position_obj, current_day_index) -> bool:
        """Trigger logic for candlestick color.

        Args:
            key (str): The key value of the trigger.
            value (dict): The value of the trigger.
            data_manager (any): The data API object.
            position_obj (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the trigger was hit.
        """
        log.debug('Checking candle stick trigger...')

        # find out how many keys there are (value is a dict)
        num_keys = len(value)

        # these will both need to be in ascending order [today, yesterday...]
        trigger_colors = []
        actual_colors = []

        # build the trigger list
        for value_key in sorted(value.keys()):
            trigger_colors.append(value[value_key])

        # build the actual list
        for i in range(num_keys):
            actual_colors.append(data_manager.get_data_point(data_manager.COLOR, current_day_index-i))

        # check for trigger
        if actual_colors == trigger_colors:
            log.info('Candle stick trigger hit!')
            return True

        log.debug('All candle stick trigger checked')

        # catch all case if nothing was hit (which is ok!)
        return False
