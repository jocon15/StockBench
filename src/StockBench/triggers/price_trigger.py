import re
import logging
from StockBench.triggers.trigger import Trigger

log = logging.getLogger()


class PriceTrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol)

    def check_trigger(self, _key, _value, data_obj, position_obj, current_day_index) -> bool:
        """Abstracted logic for stochastic oscillator triggers.

        Args:
            _key (str): The key value of the trigger.
            _value (str): The value of the trigger.
            data_obj (any): The data API object.
            position_obj (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the trigger was hit.

        Notes:
            This functions is internal (fxn inside fxn) which means everything in the outer
            function run() is global here
        """
        log.debug('Checking price triggers...')

        price = data_obj.get_data_point(data_obj.CLOSE, current_day_index)

        # check that the value from {key: value} has a number in it
        # this is the trigger value
        _nums = re.findall(r'\d+', _value)
        if len(_nums) == 1:
            trigger = float(_nums[0])
            operator = _value.replace(str(_nums[0]), '')
        else:
            print('Found invalid format price (invalid number found in trigger value)')
            # if no trigger value available, exit
            return False

        # trigger checks
        result = Trigger.basic_triggers_check(price, operator, trigger)

        log.debug('All Price triggers checked')

        # catch all case if nothing was hit (which is ok!)
        return result
