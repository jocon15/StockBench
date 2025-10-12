import logging
from StockBench.indicator.trigger import Trigger
from StockBench.simulation_data.data_manager import DataManager
from StockBench.position.position import Position

log = logging.getLogger()


class StopLossTrigger(Trigger):
    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=Trigger.SELL)

    def calculate_additional_days_from_rule_key(self, rule_key: str, rule_value: any) -> int:
        return 0

    def calculate_additional_days_from_rule_value(self, rule_value: any) -> int:
        return 0

    def add_indicator_data_from_rule_key(self, rule_key: str, rule_value: any, side: str, data_manager: DataManager):
        # stop loss does not require any additional data to be added to the data
        return

    def add_indicator_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        # stop loss does not require any additional data to be added to the data
        return

    def get_indicator_value_when_referenced(self, rule_value: str, data_manager: DataManager, current_day_index: int) -> float:
        raise NotImplementedError('Stop loss cannot be referenced in a rule value!')

    def check_trigger(self, rule_key: str, rule_value: any, data_manager: DataManager, position: Position,
                      current_day_index: int) -> bool:
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
