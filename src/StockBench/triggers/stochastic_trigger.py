import logging
from StockBench.triggers.trigger import Trigger
from StockBench.constants import *

log = logging.getLogger()


class StochasticTrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol)

    def check_trigger(self, key, value, data_obj, position_obj, current_day_index) -> bool:
        """Trigger logic for stochastic oscillator.

        Args:
            key (str): The key value of the trigger.
            value (str): The value of the trigger.
            data_obj (any): The data API object.
            position_obj (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the trigger was hit.
        """
        log.debug('Checking stochastic oscillator triggers...')
        # get the RSI value for current day
        # old way where we calculate it on the spot (deprecated)
        # rsi = self.__indicators_API.RSI(_num, current_day_index)
        # new way where we just pull the pre-calculated value from the col in the df
        stochastic = data_obj.get_data_point('stochastic_oscillator', current_day_index)

        if CURRENT_PRICE_SYMBOL in value:
            trigger_value = float(data_obj.get_data_point(data_obj.CLOSE, current_day_index))
            operator = value.replace(CURRENT_PRICE_SYMBOL, '')
        else:
            # check that the value from {key: value} has a number in it
            try:
                trigger_value = Trigger.find_numeric_in_str(value)
                operator = Trigger.find_operator_in_str(value)
            except ValueError:
                # an exception occurred trying to parse trigger value or operator
                # return false (skip trigger)
                return False

        # trigger checks
        result = Trigger.basic_triggers_check(stochastic, operator, trigger_value)

        log.debug('All stochastic triggers checked')

        return result
