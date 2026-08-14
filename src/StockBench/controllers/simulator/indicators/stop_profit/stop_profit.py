from .trigger import StopProfitTrigger
from StockBench.controllers.simulator.indicator.indicator_interface import IndicatorInterface


class StopProfitIndicator(IndicatorInterface):
    def __init__(self):
        self.__data_name = 'stop_profit'
        self.__strategy_name = self.__data_name
        self.__trigger = StopProfitTrigger(self.__strategy_name)

    def strategy_name(self):
        return self.__strategy_name

    def dataframe_name(self):
        return self.__data_name

    def trigger(self):
        return self.__trigger

    def subplot(self):
        # note: does not have a subplot
        return None
