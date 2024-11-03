import logging
from StockBench.indicator.trigger import Trigger

log = logging.getLogger()


class StopLossTrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol, side=Trigger.SELL)

    def additional_days(self, key, value) -> int:
        """Calculate the additional days required.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from the strategy.
        """
        # note stop loss does not require additional days
        return 0

    def add_to_data(self, key, value, side, data_manager):
        """Add data to the dataframe.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (any): The data object.
        """
        # note stop loss algorithm is not an additional indicator and does not
        # require any additional data to be added to the data
        return

    def check_trigger(self, key, value, data_manager, position, current_day_index) -> bool:
        """Trigger logic for stop loss.

        Args:
            key (str): The key value of the algorithm.
            value (str): The value of the algorithm.
            data_manager (any): The data API object.
            position (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the algorithm was hit.
        """
        log.debug('Checking stop loss algorithm...')

        # get the current price
        current_price = data_manager.get_data_point(data_manager.CLOSE, current_day_index)
        open_price = data_manager.get_data_point(data_manager.OPEN, current_day_index)

        # get the profit/loss values from the position
        intraday_pl = position.intraday_profit_loss(open_price, current_price)
        lifetime_pl = position.profit_loss(current_price)

        # get the profit/loss percents from the position
        intraday_plpc = position.intraday_profit_loss_percent(open_price, current_price)
        lifetime_plpc = position.profit_loss_percent(current_price)

        if 'intraday' in key:
            if intraday_pl < 0:
                if '%' in value:
                    return self.__check_plpc_loss(value, intraday_plpc)
                else:
                    return self.__check_pl_loss(value, intraday_pl)
        else:
            if lifetime_pl < 0:
                if '%' in value:
                    return self.__check_plpc_loss(value, lifetime_plpc)
                else:
                    return self.__check_pl_loss(value, lifetime_pl)

        log.debug('Stop loss algorithm checked')
        return False

    @staticmethod
    def __check_plpc_loss(value: str, plpc_value: float) -> bool:
        nums = Trigger.find_all_nums_in_str(value)
        trigger_value = float(nums[0])
        if abs(plpc_value) >= trigger_value:
            log.info('Stop loss algorithm hit!')
            return True
        return False

    @staticmethod
    def __check_pl_loss(value: str, pl_value: float) -> bool:
        trigger_value = float(value)
        if abs(pl_value) >= trigger_value:
            log.info('Stop loss algorithm hit!')
            return True
        return False
