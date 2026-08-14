from .trigger import SMATrigger
from .subplot import SMASubplot
from StockBench.controllers.simulator.indicator.indicator import IndicatorInterface


class SMAIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'SMA'
        self.__data_name = self.__strategy_name
        self.__trigger = SMATrigger(self.__strategy_name)
        self.__subplot = SMASubplot()

    def strategy_name(self):
        return self.__strategy_name

    def dataframe_name(self):
        return self.__data_name

    def trigger(self):
        return self.__trigger

    def subplot(self):
        return self.__subplot
