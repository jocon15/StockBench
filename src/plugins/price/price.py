from StockBench.plugin.plugin import PluginInterface
from .trigger import PriceTrigger
from .subplot import OHLCSubplot


class PricePlugin(PluginInterface):
    def __init__(self):
        self.__strategy_name = 'price'
        self.__data_name = self.__strategy_name
        self.__trigger = PriceTrigger(self.__strategy_name)
        self.__subplot = OHLCSubplot()

    def get_strategy_name(self):
        return self.__strategy_name

    def get_data_name(self):
        return self.__data_name

    def get_trigger(self):
        return self.__trigger

    def get_subplot(self):
        return self.__subplot
