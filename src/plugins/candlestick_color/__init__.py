"""Plugin for candlestick colors."""
from StockBench.plugin.plugin import PluginManager
from .candlestick_color import CandlestickColorPlugin


def initialize():
    PluginManager.register('candlestick_color_plugin', CandlestickColorPlugin)
    return {'candlestick_color_plugin': CandlestickColorPlugin}

