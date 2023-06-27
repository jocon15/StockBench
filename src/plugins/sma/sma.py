
"""
This sma plugin class is a subclass of the plugin class and implements its abstract methods.

This class should instantiate the trigger and subplot subclasses defined in the other files in this plugin.
The subclass instances should be kept as attributes [member variables] of this class.
The core code interacts with the subplots through this plugin interface.


The way that the internet, https://alysivji.github.io/simple-plugin-system.html, describes it is to have a part
of the core code be like:

    for plugin in plugins:
        plugin.some_fxn(...)

where you give the plugins an opportunity to add, subtract, append... perform their own logic.

You can pass the plugins certain resources like objects or data to help the plugin be useful.

Just remember that every plugin you call in this style must have that function available.
BUT!!! There are ways that you can filter out plugins that may not have the functionality, for example,
using the isInstance function or other identifying features of plugins, which are just objects.

"""
from StockBench.plugin.plugin import PluginInterface
from .trigger import SMATrigger
from .subplot import DummySubplot


class SMAPlugin(PluginInterface):
    def __init__(self):
        self.__strategy_name = 'SMA'
        self.__data_name = self.__strategy_name
        self.__trigger = SMATrigger(self.__strategy_name)
        self.__subplot = DummySubplot()

    def get_strategy_name(self):
        return self.__strategy_name

    def get_data_name(self):
        return self.__data_name

    def get_trigger(self):
        return self.__trigger

    def get_subplot(self):
        return self.__subplot
