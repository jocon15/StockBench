"""Plugin for the stop profit"""
from StockBench.plugin.plugin import PluginManager
from .stop_profit import StopProfitPlugin


def initialize():
    PluginManager.register('stop_profit_plugin', StopProfitPlugin)
    return {'stop_profit_plugin': StopProfitPlugin}
