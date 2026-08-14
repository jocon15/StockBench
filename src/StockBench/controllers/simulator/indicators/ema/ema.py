from .trigger import EMATrigger
from .subplot import EMASubplot
from StockBench.controllers.simulator.indicator.indicator import IndicatorInterface


class EMAIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'EMA'
        self.__data_name = self.__strategy_name
        self.__trigger = EMATrigger(self.__strategy_name)
        self.__subplot = EMASubplot()

    def strategy_name(self):
        return self.__strategy_name

    def data_name(self):
        return self.__data_name

    def trigger(self):
        return self.__trigger

    def subplot(self):
        return self.__subplot
