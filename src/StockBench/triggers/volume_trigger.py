import re
import logging
from StockBench.triggers.trigger import Trigger
from StockBench.constants import *

log = logging.getLogger()


class VolumeTrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol)

    def check_trigger(self, _key, _value, data_obj, position_obj, current_day_index) -> bool:
        """"""
        volume = data_obj.get_data_point(data_obj.VOLUME, current_day_index)

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
                print('Found invalid format SMA (invalid number found in trigger value)')
                # if no trigger value available, exit
                return False

        # trigger checks
        result = Trigger.basic_triggers_check(volume, operator, trigger)

        log.debug('All volume triggers checked')

        return result
