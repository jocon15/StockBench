import logging
from StockBench.triggers.trigger import Trigger

log = logging.getLogger()


class CandlestickColorTrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol)

    def check_trigger(self, _key, _value, data_obj, position_obj, current_day_index) -> bool:
        """Abstracted logic for candle stick triggers.

        Args:
            _key (str): The key value of the trigger.
            _value (dict): The value of the trigger.
            data_obj (any): The data API object.
            position_obj (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the trigger was hit.

        Notes:
            This functions is internal (fxn inside fxn) which means everything in the outer
            function run() is global here.
        """
        log.debug('Checking candle stick triggers...')

        # find out how many keys there are (_value is a dict)
        num_keys = len(_value)

        # these will both need to be in ascending order [today, yesterday...]
        trigger_colors = list()
        actual_colors = list()

        # build the trigger list
        for _key in sorted(_value.keys()):
            candle_color = _value[_key]
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
