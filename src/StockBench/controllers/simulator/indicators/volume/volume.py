from .setup import VolumeSetup
from .rule import VolumeRule
from .subplot import VolumeSubplot
from StockBench.controllers.simulator.indicator.indicator_interface import IndicatorInterface


class VolumeIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_name = 'volume'
        self.__data_name = self.__strategy_name
        self.__setup = VolumeSetup(self.__strategy_name)
        self.__rule = VolumeRule(self.__strategy_name)
        self.__subplot = VolumeSubplot()

    def strategy_name(self) -> str:
        return self.__strategy_name

    def dataframe_name(self) -> str:
        return self.__data_name

    @property
    def setup(self) -> VolumeSetup:
        return self.__setup

    @property
    def rule(self) -> VolumeRule:
        return self.__rule

    @property
    def subplot(self) -> VolumeSubplot:
        return self.__subplot
