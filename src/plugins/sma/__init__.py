"""Plugin for simple moving average."""

from StockBench.plugin.plugin import PluginManager
from .sma import SMAPlugin


def initialize():
    PluginManager.register('sma_plugin', SMAPlugin)
    return {'sma_plugin': SMAPlugin}
