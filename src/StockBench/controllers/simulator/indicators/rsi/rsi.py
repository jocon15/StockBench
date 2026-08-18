from StockBench.controllers.simulator.indicator.indicator_interface import IndicatorInterface
from .setup import RSISetup
from .rule import RSIRule
from .subplot import RSISubplot


class RSIIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'RSI'
        self.__data_name = self.__strategy_name
        self.__setup = RSISetup(self.__strategy_name)
        self.__rule = RSIRule(self.__strategy_name)
        self.__subplot = RSISubplot()

    def strategy_name(self) -> str:
        return self.__strategy_name

    def dataframe_name(self) -> str:
        return self.__data_name

    @property
    def setup(self) -> RSISetup:
        return self.__setup

    @property
    def rule(self) -> RSIRule:
        return self.__rule

    @property
    def subplot(self) -> RSISubplot:
        return self.__subplot
