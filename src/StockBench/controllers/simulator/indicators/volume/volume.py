from .trigger import VolumeTrigger
from .subplot import VolumeSubplot
from StockBench.controllers.simulator.indicator.indicator import IndicatorInterface


class VolumeIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'volume'
        self.__data_name = self.__strategy_name
        self.__trigger = VolumeTrigger(self.__strategy_name)
        self.__subplot = VolumeSubplot()

    def strategy_name(self):
        return self.__strategy_name

    def data_name(self):
        return self.__data_name

    def trigger(self):
        return self.__trigger

    def subplot(self):
        return self.__subplot
