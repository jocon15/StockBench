import logging
from StockBench.indicator.trigger import Trigger
from StockBench.simulation_data.data_manager import DataManager
from StockBench.position.position import Position

log = logging.getLogger()


class StopProfitTrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol, side=Trigger.SELL)

    def additional_days(self, rule_key: str, value_value: str) -> int:
        """Calculate the additional days required.

        Args:
            rule_key: The key value from the strategy.
            value_value: The value from the strategy.
        """
        # note stop profit does not require additional days
        return 0

    def add_to_data(self, rule_key: str, rule_value: str, side: str, data_manager: DataManager):
        """Add data to the dataframe.

        Args:
            rule_key (any): The key value from the strategy.
            rule_value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (DataManager): The data object.
        """
        # note stop profit algorithm is not an additional indicator and does not
        # require any additional data to be added to the data
        return

    def check_trigger(self, rule_key, rule_value, data_manager, position, current_day_index) -> bool:
        """Trigger logic for stop profit.

        Args:
            rule_key (str): The key value of the algorithm.
            rule_value (str): The value of the algorithm.
            data_manager (DataManager): The data API object.
            position (Position): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if a trigger was hit.
        """
        log.debug('Checking stop profit algorithm...')

        current_price = data_manager.get_data_point(data_manager.CLOSE, current_day_index)
        open_price = data_manager.get_data_point(data_manager.OPEN, current_day_index)

        intraday_pl = position.intraday_profit_loss(open_price, current_price)
        lifetime_pl = position.profit_loss(current_price)

        intraday_plpc = position.intraday_profit_loss_percent(open_price, current_price)
        lifetime_plpc = position.profit_loss_percent(current_price)

        if 'intraday' in rule_key:
            if intraday_pl > 0:
                if '%' in rule_value:
                    return self.__check_plpc_profit(rule_value, intraday_plpc)
                else:
                    return self.__check_pl_profit(rule_value, intraday_pl)
        else:
            if lifetime_pl > 0:
                if '%' in rule_value:
                    return self.__check_plpc_profit(rule_value, lifetime_plpc)
                else:
                    return self.__check_pl_profit(rule_value, lifetime_pl)

        log.debug('Stop profit algorithm checked')
        return False

    @staticmethod
    def __check_plpc_profit(value: str, plpc_value: float) -> bool:
        """Check stop profit/loss percent."""
        nums = Trigger.find_all_nums_in_str(value)
        trigger_value = float(nums[0])
        if plpc_value >= trigger_value:
            log.info('Stop profit algorithm hit!')
            return True
        return False

    @staticmethod
    def __check_pl_profit(value: str, pl_value: float) -> bool:
        """Check stop profit/loss."""
        trigger_value = float(value)
        if pl_value >= trigger_value:
            log.info('Stop profit algorithm hit!')
            return True
        return False
