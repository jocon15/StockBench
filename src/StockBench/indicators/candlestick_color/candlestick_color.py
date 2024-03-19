from .trigger import CandlestickColorTrigger
from StockBench.indicator.indicator import IndicatorInterface


class CandlestickColorIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'color'
        self.__data_name = self.__strategy_name
        self.__trigger = CandlestickColorTrigger(self.__strategy_name)

    def get_strategy_name(self):
        return self.__strategy_name

    def get_data_name(self):
        return self.__data_name

    def get_trigger(self):
        return self.__trigger

    def get_subplot(self):
        # note: candlestick colors do not have a subplot
        return None
