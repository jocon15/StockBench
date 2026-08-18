import logging

from typing import Union

from StockBench.controllers.simulator.indicator.trigger_interface import TriggerInterface
from StockBench.controllers.simulator.indicator.exceptions import StrategyIndicatorError
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager
from StockBench.models.position.position import Position

log = logging.getLogger()


class CandlestickColorTrigger(TriggerInterface):
    def __init__(self, indicator_symbol):
        super().__init__(indicator_symbol, side=TriggerInterface.AGNOSTIC)

    def get_indicator_value_when_referenced(self, rule_value: str, data_manager: DataManager,
                                            current_day_index: int) -> float:
        raise NotImplementedError('Candlestick color cannot be referenced in a rule value!')

    def check_trigger(self, rule_key: str, rule_value: Union[str, int, dict], data_manager: DataManager,
                      position: Position, current_day_index: int) -> bool:
        log.debug('Checking candle stick algorithm...')

        key_count = len(rule_value)

        if key_count == 0:
            raise StrategyIndicatorError(f'{self.indicator_symbol} key: {rule_key} must have at least one color child '
                                         f'key')

        trigger_colors = [rule_value[value_key] for value_key in sorted(rule_value.keys())]
        actual_colors = [data_manager.get_data_point(data_manager.COLOR, current_day_index-i) for i in range(key_count)]

        if actual_colors == trigger_colors:
            log.info('Candle stick algorithm hit!')
            return True

        log.debug('All candle stick algorithm checked')

        return False
