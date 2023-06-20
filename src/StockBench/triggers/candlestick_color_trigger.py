import logging
from StockBench.triggers.trigger import Trigger

log = logging.getLogger()


class CandlestickColorTrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol)

    def additional_days(self, key) -> int:
        """Calculate the additional days required.

        Args:
            key (any): The key value from the strategy.
        """
        # note candle colors does not require any additional days
        return 0

    def add_to_data(self, key, value, side, data_obj):
        """Add data to the dataframe.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_obj (any): The data object.
        """
        # candle colors are included by default
        return

    def check_trigger(self, key, value, data_obj, position_obj, current_day_index) -> bool:
        """Trigger logic for candlestick color.

        Args:
            key (str): The key value of the trigger.
            value (dict): The value of the trigger.
            data_obj (any): The data API object.
            position_obj (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the trigger was hit.
        """
        log.debug('Checking candle stick triggers...')

        # find out how many keys there are (_value is a dict)
        num_keys = len(value)

        # these will both need to be in ascending order [today, yesterday...]
        trigger_colors = list()
        actual_colors = list()

        # build the trigger list
        for _key in sorted(value.keys()):
            candle_color = value[_key]
            if candle_color == 'green':
                trigger_colors.append(1)
            else:
                trigger_colors.append(0)

        # build the actual list
        for i in range(num_keys):
            actual_colors.append(data_obj.get_data_point(data_obj.COLOR, current_day_index))

        # check for trigger
        if actual_colors == trigger_colors:
            log.info('Candle stick trigger hit!')
            return True

        log.debug('All candle stick triggers checked')

        # catch all case if nothing was hit (which is ok!)
        return False
