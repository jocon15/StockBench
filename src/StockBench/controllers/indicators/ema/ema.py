from .trigger import EMATrigger
from .subplot import EMASubplot
from StockBench.controllers.indicator import IndicatorInterface


class EMAIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'EMA'
        self.__data_name = self.__strategy_name
        self.__trigger = EMATrigger(self.__strategy_name)
        self.__subplot = EMASubplot()

    def get_strategy_name(self):
        return self.__strategy_name

    def get_data_name(self):
        return self.__data_name

    def get_trigger(self):
        return self.__trigger

    def get_subplot(self):
        return self.__subplot
