from .setup import SMASetup
from .rule import SMARule
from .subplot import SMASubplot
from StockBench.controllers.simulator.indicator.indicator_interface import IndicatorInterface


class SMAIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'SMA'
        self.__data_name = self.__strategy_name
        self.__setup = SMASetup(self.__strategy_name)
        self.__rule = SMARule(self.__strategy_name)
        self.__subplot = SMASubplot()

    def strategy_name(self) -> str:
        return self.__strategy_name

    def dataframe_name(self) -> str:
        return self.__data_name

    @property
    def setup(self) -> SMASetup:
        return self.__setup

    @property
    def rule(self) -> SMARule:
        return self.__rule

    @property
    def subplot(self) -> SMASubplot:
        return self.__subplot
