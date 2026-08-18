from .setup import StopLossSetup
from .rule import StopLossRule
from StockBench.controllers.simulator.indicator.indicator_interface import IndicatorInterface


class StopLossIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'stop_loss'
        self.__data_name = self.__strategy_name
        self.__setup = StopLossSetup(self.__strategy_name)
        self.__trigger = StopLossRule(self.__strategy_name)

    def strategy_name(self):
        return self.__strategy_name

    def dataframe_name(self):
        return self.__data_name

    @property
    def setup(self) -> StopLossSetup:
        return self.__setup

    @property
    def rule(self):
        return self.__trigger

    @property
    def subplot(self):
        # note: does not have a subplot
        return None
