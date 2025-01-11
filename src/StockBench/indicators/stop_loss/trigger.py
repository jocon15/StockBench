import logging
from StockBench.indicator.trigger import Trigger
from StockBench.simulation_data.data_manager import DataManager
from StockBench.position.position import Position

log = logging.getLogger()


class StopLossTrigger(Trigger):
    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=Trigger.SELL)

    def additional_days_from_rule_key(self, rule_key, rule_value) -> int:
        """Calculate the additional days required.

        Args:
            rule_key (any): The key value from the strategy.
            rule_value (any): The value from the strategy.
        """
        # note stop loss does not require additional days
        return 0

    def add_to_data(self, rule_key, rule_value, side, data_manager):
        """Add data to the dataframe.

        Args:
            rule_key (any): The key value from the strategy.
            rule_value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (DataManager): The data object.
        """
        # note stop loss algorithm is not an additional indicator and does not
        # require any additional data to be added to the data
        return

    def check_trigger(self, rule_key, rule_value, data_manager, position, current_day_index) -> bool:
        """Trigger logic for stop loss.

        Args:
            rule_key (str): The key value of the algorithm.
            rule_value (str): The value of the algorithm.
            data_manager (DataManager): The data API object.
            position (Position): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if a trigger was hit.
        """
        log.debug('Checking stop loss algorithm...')

        current_price = data_manager.get_data_point(data_manager.CLOSE, current_day_index)
        open_price = data_manager.get_data_point(data_manager.OPEN, current_day_index)

        intraday_pl = position.intraday_profit_loss(open_price, current_price)
        lifetime_pl = position.profit_loss(current_price)

        intraday_plpc = position.intraday_profit_loss_percent(open_price, current_price)
        lifetime_plpc = position.profit_loss_percent(current_price)

        if 'intraday' in rule_key:
            if intraday_pl < 0:
                if '%' in rule_value:
                    return self.__check_plpc_loss(rule_value, intraday_plpc)
                else:
                    return self.__check_pl_loss(rule_value, intraday_pl)
        else:
            if lifetime_pl < 0:
                if '%' in rule_value:
                    return self.__check_plpc_loss(rule_value, lifetime_plpc)
                else:
                    return self.__check_pl_loss(rule_value, lifetime_pl)

        log.debug('Stop loss algorithm checked')
        return False

    @staticmethod
    def __check_plpc_loss(value: str, plpc_value: float) -> bool:
        """Check stop loss trigger for profit/loss percent."""
        nums = Trigger.find_all_nums_in_str(value)
        trigger_value = float(nums[0])
        if abs(plpc_value) >= trigger_value:
            log.info('Stop loss algorithm hit!')
            return True
        return False

    @staticmethod
    def __check_pl_loss(value: str, pl_value: float) -> bool:
        """Check stop loss trigger for profit/loss."""
        trigger_value = float(value)
        if abs(pl_value) >= trigger_value:
            log.info('Stop loss algorithm hit!')
            return True
        return False
