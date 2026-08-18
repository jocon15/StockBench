from .setup import EMASetup
from .rule import EMARule
from .subplot import EMASubplot
from StockBench.controllers.simulator.indicator.indicator_interface import IndicatorInterface


class EMAIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'EMA'
        self.__data_name = self.__strategy_name
        self.__setup = EMASetup(self.__strategy_name)
        self.__trigger = EMARule(self.__strategy_name)
        self.__subplot = EMASubplot()

    def strategy_name(self):
        return self.__strategy_name

    def dataframe_name(self):
        return self.__data_name

    @property
    def setup(self) -> EMASetup:
        return self.__setup

    @property
    def rule(self):
        return self.__trigger

    @property
    def subplot(self):
        return self.__subplot
