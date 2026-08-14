from .trigger import MACDTrigger
from .subplot import MACDSubplot
from StockBench.controllers.simulator.indicator.indicator import IndicatorInterface


class MACDIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'MACD'
        self.__data_name = self.__strategy_name
        self.__trigger = MACDTrigger(self.__strategy_name)
        self.__subplot = MACDSubplot()

    def strategy_name(self):
        return self.__strategy_name

    def dataframe_name(self):
        return self.__data_name

    def trigger(self):
        return self.__trigger

    def subplot(self):
        return self.__subplot
