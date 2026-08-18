from .setup import EMASetup
from .rule import EMARule
from .subplot import EMASubplot
from StockBench.controllers.simulator.indicator.indicator_interface import IndicatorInterface


class EMAIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'EMA'
        self.__data_name = self.__strategy_name
        self.__setup = EMASetup(self.__strategy_name)
        self.__rule = EMARule(self.__strategy_name)
        self.__subplot = EMASubplot()

    def strategy_name(self) -> str:
        return self.__strategy_name

    def dataframe_name(self) -> str:
        return self.__data_name

    @property
    def setup(self) -> EMASetup:
        return self.__setup

    @property
    def rule(self) -> EMARule:
        return self.__rule

    @property
    def subplot(self) -> EMASubplot:
        return self.__subplot
