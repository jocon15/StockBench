from StockBench.controllers.simulator.indicator.indicator import IndicatorInterface
from .trigger import RSITrigger
from .subplot import RSISubplot


class RSIIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'RSI'
        self.__data_name = self.__strategy_name
        self.__trigger = RSITrigger(self.__strategy_name)
        self.__subplot = RSISubplot()

    def strategy_name(self):
        return self.__strategy_name

    def data_name(self):
        return self.__data_name

    def trigger(self):
        return self.__trigger

    def subplot(self):
        return self.__subplot
