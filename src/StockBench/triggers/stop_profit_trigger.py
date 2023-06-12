import logging
from StockBench.triggers.trigger import Trigger

log = logging.getLogger()


class StopProfitTrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol)

    def check_trigger(self, key, value, data_obj, position_obj, current_day_index) -> bool:
        """Trigger logic for stop profit.

        Args:
            key (str): The key value of the trigger.
            value (str): The value of the trigger.
            data_obj (any): The data API object.
            position_obj (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the trigger was hit.
        """
        log.debug('Checking stop profit triggers...')

        # get the trigger from the strategy
        trigger_value = float(value)

        # get the current price
        price = data_obj.get_data_point(data_obj.CLOSE, current_day_index)

        # get the profit/loss from the strategy
        p_l = position_obj.profit_loss(price)

        # check for profit
        if p_l > 0:
            # check for trigger
            if p_l >= trigger_value:
                log.info('Stop profit trigger hit!')
                return True

        log.debug('Stop profit triggers checked')

        # trigger was not hit
        return False
