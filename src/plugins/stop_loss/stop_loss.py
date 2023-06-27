from StockBench.plugin.plugin import PluginInterface
from .trigger import StopLossTrigger


class StopLossPlugin(PluginInterface):
    def __init__(self):
        self.__strategy_name = 'stop_loss'
        self.__data_name = self.__strategy_name
        self.__trigger = StopLossTrigger(self.__strategy_name)

    def get_strategy_name(self):
        return self.__strategy_name

    def get_data_name(self):
        return self.__data_name

    def get_trigger(self):
        return self.__trigger

    def get_subplot(self):
        # note: does not have a subplot
        return None
