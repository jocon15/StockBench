from .setup import StopProfitSetup
from .rule import StopProfitRule
from StockBench.controllers.simulator.indicator.indicator_interface import IndicatorInterface


class StopProfitIndicator(IndicatorInterface):
    def __init__(self):
        self.__data_name = 'stop_profit'
        self.__strategy_name = self.__data_name
        self.__setup = StopProfitSetup(self.__strategy_name)
        self._rule = StopProfitRule(self.__strategy_name)

    def strategy_name(self) -> str:
        return self.__strategy_name

    def dataframe_name(self) -> str:
        return self.__data_name

    @property
    def setup(self) -> StopProfitSetup:
        return self.__setup

    @property
    def rule(self) -> StopProfitRule:
        return self._rule

    @property
    def subplot(self):
        # note: does not have a subplot
        return None
