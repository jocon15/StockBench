"""Plugin for relative strength index."""

from StockBench.plugin.plugin import PluginManager
from .rsi import RSIPlugin


def initialize():
    PluginManager.register('rsi_plugin', RSIPlugin)
    return {'rsi_plugin': RSIPlugin}
