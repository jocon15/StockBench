"""Plugin for exponential moving average."""
from StockBench.plugin.plugin import PluginManager
from .ema import EMAPlugin


def initialize():
    PluginManager.register('ema_plugin', EMAPlugin)
    return {'ema_plugin': EMAPlugin}
