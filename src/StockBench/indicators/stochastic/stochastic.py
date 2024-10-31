from StockBench.indicator.indicator import IndicatorInterface
from .subplot import StochasticSubplot
from .trigger import StochasticTrigger


class StochasticIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'stochastic'
        self.__data_name = self.__strategy_name
        self.__trigger = StochasticTrigger(self.__strategy_name)
        self.__subplot = StochasticSubplot()

    def get_strategy_name(self):
        return self.__strategy_name

    def get_data_name(self):
        return self.__data_name

    def get_trigger(self):
        return self.__trigger

    def get_subplot(self):
        return self.__subplot
