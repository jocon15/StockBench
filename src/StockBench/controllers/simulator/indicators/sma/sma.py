from .trigger import SMATrigger
from .subplot import SMASubplot
from StockBench.controllers.simulator.indicator import IndicatorInterface


class SMAIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'SMA'
        self.__data_name = self.__strategy_name
        self.__trigger = SMATrigger(self.__strategy_name)
        self.__subplot = SMASubplot()

    def get_strategy_name(self):
        return self.__strategy_name

    def get_data_name(self):
        return self.__data_name

    def get_trigger(self):
        return self.__trigger

    def get_subplot(self):
        return self.__subplot
