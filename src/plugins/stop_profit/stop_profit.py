from .trigger import StopProfitTrigger
from StockBench.plugin.plugin_interface import PluginInterface


class StopProfitPlugin(PluginInterface):
    def __init__(self):
        self.__data_name = 'stop_profit'
        self.__strategy_name = self.__data_name
        self.__trigger = StopProfitTrigger(self.__strategy_name)

    def get_strategy_name(self):
        return self.__strategy_name

    def get_data_name(self):
        return self.__data_name

    def get_trigger(self):
        return self.__trigger

    def get_subplot(self):
        # note: does not have a subplot
        return None
