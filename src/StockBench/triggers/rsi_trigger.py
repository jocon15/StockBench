import re
import logging
from StockBench.triggers.trigger import Trigger
from StockBench.constants import *

log = logging.getLogger()


class RSITrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol)

    def check_trigger(self, _key, _value, data_obj, position_obj, current_day_index) -> bool:
        """Abstracted logic for RSI triggers.

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
        log.debug('Checking stochastic oscillator triggers...')

        # find the value of the RSI else default
        _num = DEFAULT_RSI_LENGTH
        _nums = re.findall(r'\d+', _key)
        if len(_nums) == 1:
            _num = float(_nums[0])

        # get the RSI value for current day
        # old way where we calculate it on the spot (deprecated)
        # rsi = self.__indicators_API.RSI(_num, current_day_index)
        # new way where we just pull the pre-calculated value from the col in the df
        rsi = data_obj.get_data_point('RSI', current_day_index)

        if CURRENT_PRICE_SYMBOL in _value:
            trigger = float(data_obj.get_data_point(data_obj.CLOSE, current_day_index))
            operator = _value.replace(CURRENT_PRICE_SYMBOL, '')
        else:
            # check that the value from {key: value} has a number in it
            # this is the trigger value
            _nums = re.findall(r'\d+', _value)
            if len(_nums) == 1:
                trigger = float(_nums[0])
                operator = _value.replace(str(_nums[0]), '')
            else:
                log.warning('Found invalid format rsi (invalid number found in trigger value)')
                print('Found invalid format rsi (invalid number found in trigger value)')
                # if no trigger value available, exit
                return False

        # trigger checks
        result = Trigger.basic_triggers_check(rsi, operator, trigger)

        log.debug('All RSI triggers checked')

        return result
