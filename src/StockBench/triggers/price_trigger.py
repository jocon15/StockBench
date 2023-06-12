import logging
from StockBench.triggers.trigger import Trigger

log = logging.getLogger()


class PriceTrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol)

    def check_trigger(self, key, value, data_obj, position_obj, current_day_index) -> bool:
        """Trigger logic for price.

        Args:
            key (str): The key value of the trigger.
            value (str): The value of the trigger.
            data_obj (any): The data API object.
            position_obj (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the trigger was hit.
        """
        log.debug('Checking price triggers...')

        price = data_obj.get_data_point(data_obj.CLOSE, current_day_index)

        # check that the value from {key: value} has a number in it
        # this is the trigger value
        # check that the value from {key: value} has a number in it
        try:
            trigger_value = Trigger.find_numeric_in_str(value)
            operator = Trigger.find_operator_in_str(value)
        except ValueError:
            # an exception occurred trying to parse trigger value or operator
            # return false (skip trigger)
            return False

        # trigger checks
        result = Trigger.basic_triggers_check(price, operator, trigger_value)

        log.debug('All Price triggers checked')

        # catch all case if nothing was hit (which is ok!)
        return result
