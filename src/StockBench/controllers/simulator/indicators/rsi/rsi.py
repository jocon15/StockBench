from StockBench.controllers.simulator.indicator.indicator_interface import IndicatorInterface
from .setup import RSISetup
from .trigger import RSITrigger
from .subplot import RSISubplot


class RSIIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'RSI'
        self.__data_name = self.__strategy_name
        self.__setup = RSISetup(self.__strategy_name)
        self.__trigger = RSITrigger(self.__strategy_name)
        self.__subplot = RSISubplot()

    def strategy_name(self):
        return self.__strategy_name

    def dataframe_name(self):
        return self.__data_name

    @property
    def setup(self) -> RSISetup:
        return self.__setup

    def trigger(self):
        return self.__trigger

    def subplot(self):
        return self.__subplot
