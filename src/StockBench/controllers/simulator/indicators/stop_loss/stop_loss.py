from .setup import StopLossSetup
from .trigger import StopLossTrigger
from StockBench.controllers.simulator.indicator.indicator_interface import IndicatorInterface


class StopLossIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'stop_loss'
        self.__data_name = self.__strategy_name
        self.__setup = StopLossSetup(self.__strategy_name)
        self.__trigger = StopLossTrigger(self.__strategy_name)

    def strategy_name(self):
        return self.__strategy_name

    def dataframe_name(self):
        return self.__data_name

    @property
    def setup(self) -> StopLossSetup:
        return self.__setup

    def trigger(self):
        return self.__trigger

    def subplot(self):
        # note: does not have a subplot
        return None
