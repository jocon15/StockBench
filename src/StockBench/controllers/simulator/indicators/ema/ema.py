from .setup import EMASetup
from .trigger import EMATrigger
from .subplot import EMASubplot
from StockBench.controllers.simulator.indicator.indicator_interface import IndicatorInterface


class EMAIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'EMA'
        self.__data_name = self.__strategy_name
        self.__setup = EMASetup(self.__strategy_name)
        self.__trigger = EMATrigger(self.__strategy_name)
        self.__subplot = EMASubplot()

    def strategy_name(self):
        return self.__strategy_name

    def dataframe_name(self):
        return self.__data_name

    @property
    def setup(self) -> EMASetup:
        return self.__setup

    def trigger(self):
        return self.__trigger

    def subplot(self):
        return self.__subplot
