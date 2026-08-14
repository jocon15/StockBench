from StockBench.controllers.simulator.indicator.indicator import IndicatorInterface
from .subplot import StochasticSubplot
from .trigger import StochasticTrigger


class StochasticIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'stochastic'
        self.__data_name = self.__strategy_name
        self.__trigger = StochasticTrigger(self.__strategy_name)
        self.__subplot = StochasticSubplot()

    def strategy_name(self):
        return self.__strategy_name

    def dataframe_name(self):
        return self.__data_name

    def trigger(self):
        return self.__trigger

    def subplot(self):
        return self.__subplot
