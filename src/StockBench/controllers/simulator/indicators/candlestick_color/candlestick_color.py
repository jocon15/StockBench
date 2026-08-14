from .trigger import CandlestickColorTrigger
from StockBench.controllers.simulator.indicator.indicator import IndicatorInterface


class CandlestickColorIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'color'
        self.__data_name = self.__strategy_name
        self.__trigger = CandlestickColorTrigger(self.__strategy_name)

    def strategy_name(self):
        return self.__strategy_name

    def dataframe_name(self):
        return self.__data_name

    def trigger(self):
        return self.__trigger

    def subplot(self):
        # note: candlestick colors do not have a subplot
        return None
