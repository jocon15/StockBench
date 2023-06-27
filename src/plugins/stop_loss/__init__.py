"""Plugin for the stop loss."""
from StockBench.plugin.plugin import PluginManager
from .stop_loss import StopLossPlugin


def initialize():
    PluginManager.register('stop_loss_plugin', StopLossPlugin)
    return {'stop_loss_plugin': StopLossPlugin}
