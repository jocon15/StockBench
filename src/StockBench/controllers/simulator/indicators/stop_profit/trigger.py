import logging

from StockBench.controllers.simulator.indicator.trigger import Trigger
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager
from StockBench.models.position.position import Position

log = logging.getLogger()


class StopProfitTrigger(Trigger):
    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=Trigger.SELL)

    def calculate_additional_days_from_rule_key(self, rule_key: str, rule_value: any) -> int:
        return 0

    def calculate_additional_days_from_rule_value(self, rule_value: any) -> int:
        return 0

    def add_indicator_data_from_rule_key(self, rule_key: str, rule_value, side: str, data_manager: str):
        # stop profit does not require any additional data to be added to the data
        return

    def add_indicator_data_from_rule_value(self, rule_value: str, side: str, data_manager: DataManager):
        # stop profit does not require any additional data to be added to the data
        return

    def get_indicator_value_when_referenced(self, rule_value: str, data_manager: DataManager,
                                            current_day_index: int) -> float:
        raise NotImplementedError('Stop profit cannot be referenced in a rule value!')

    def check_trigger(self, rule_key: str, rule_value: any, data_manager: DataManager, position: Position,
                      current_day_index: int) -> bool:
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
        """Checks stop profit trigger for profit percent trigger event."""
        nums = Trigger.find_all_nums_in_str(value)
        trigger_value = float(nums[0])
        if plpc_value >= trigger_value:
            log.info('Stop profit algorithm hit!')
            return True
        return False

    @staticmethod
    def __check_pl_profit(value: str, pl_value: float) -> bool:
        """Checks stop profit trigger for profit trigger event."""
        trigger_value = float(value)
        if pl_value >= trigger_value:
            log.info('Stop profit algorithm hit!')
            return True
        return False
