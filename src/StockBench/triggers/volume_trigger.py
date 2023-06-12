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
            trigger_value = float(data_obj.get_data_point(data_obj.CLOSE, current_day_index))
            operator = _value.replace(CURRENT_PRICE_SYMBOL, '')
        else:
            # check that the value from {key: value} has a number in it
            try:
                trigger_value = Trigger.find_numeric_in_str(_value)
                operator = Trigger.find_operator_in_str(_value)
            except ValueError:
                # an exception occurred trying to parse trigger value or operator
                # return false (skip trigger)
                return False

        # trigger checks
        result = Trigger.basic_triggers_check(volume, operator, trigger_value)

        log.debug('All volume triggers checked')

        return result