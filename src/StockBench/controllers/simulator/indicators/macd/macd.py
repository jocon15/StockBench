from .setup import MACDSetup
from .rule import MACDRule
from .subplot import MACDSubplot
from StockBench.controllers.simulator.indicator.indicator_interface import IndicatorInterface


class MACDIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'MACD'
        self.__data_name = self.__strategy_name
        self.__startup = MACDSetup(self.__strategy_name)
        self.__rule = MACDRule(self.__strategy_name)
        self.__subplot = MACDSubplot()

    def strategy_name(self) -> str:
        return self.__strategy_name

    def dataframe_name(self) -> str:
        return self.__data_name

    @property
    def setup(self) -> MACDSetup:
        return self.__startup

    @property
    def rule(self) -> MACDRule:
        return self.__rule

    @property
    def subplot(self) -> MACDSubplot:
        return self.__subplot
