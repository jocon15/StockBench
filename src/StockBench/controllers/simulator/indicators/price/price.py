from .setup import PriceSetup
from .subplot import OHLCSubplot
from .rule import PriceRule
from StockBench.controllers.simulator.indicator.indicator_interface import IndicatorInterface


class PriceIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'price'
        self.__data_name = self.__strategy_name
        self.__setup = PriceSetup(self.__strategy_name)
        self.__rule = PriceRule(self.__strategy_name)
        self.__subplot = OHLCSubplot()

    def strategy_name(self) -> str:
        return self.__strategy_name

    def dataframe_name(self) -> str:
        return self.__data_name

    @property
    def setup(self) -> PriceSetup:
        return self.__setup

    @property
    def rule(self) -> PriceRule:
        return self.__rule

    @property
    def subplot(self) -> OHLCSubplot:
        return self.__subplot
