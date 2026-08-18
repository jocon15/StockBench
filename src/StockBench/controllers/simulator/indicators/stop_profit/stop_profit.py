from .setup import StopProfitSetup
from .rule import StopProfitRule
from StockBench.controllers.simulator.indicator.indicator_interface import IndicatorInterface


class StopProfitIndicator(IndicatorInterface):
    def __init__(self):
        self.__data_name = 'stop_profit'
        self.__strategy_name = self.__data_name
        self.__setup = StopProfitSetup(self.__strategy_name)
        self.__trigger = StopProfitRule(self.__strategy_name)

    def strategy_name(self):
        return self.__strategy_name

    def dataframe_name(self):
        return self.__data_name

    @property
    def setup(self) -> StopProfitSetup:
        return self.__setup

    @property
    def trigger(self):
        return self.__trigger

    @property
    def subplot(self):
        # note: does not have a subplot
        return None
