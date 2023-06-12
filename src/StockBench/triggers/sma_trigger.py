import re
import logging
from StockBench.triggers.trigger import Trigger
from StockBench.constants import *

log = logging.getLogger()


class SMATrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol)

    def check_trigger(self, _key, _value, data_obj, position_obj, current_day_index) -> bool:
        """Abstracted logic for SMA triggers.

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
        log.debug('Checking SMA triggers...')

        # find the SMA length, else exit
        _nums = re.findall(r'\d+', _key)
        # since we have no default SMA, there must be a value provided, else exit
        if len(_nums) == 1:
            _num = int(_nums[0])

            # get the sma value for the current day
            # old way where we calculate it on the spot (deprecated)
            # sma = self.__indicators_API.SMA(_num, current_day_index)
            # new way where we just pull the pre-calculated value from the col in the df
            title = f'SMA{_num}'
            sma = data_obj.get_data_point(title, current_day_index)

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
            result = Trigger.basic_triggers_check(sma, operator, trigger_value)

            log.debug('All SMA triggers checked')

            return result

        log.warning(f'Warning: {_key} is in incorrect format and will be ignored')
        print(f'Warning: {_key} is in incorrect format and will be ignored')
        return False
