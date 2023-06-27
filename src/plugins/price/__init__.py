"""Plugin for price."""
from StockBench.plugin.plugin import PluginManager
from .price import PricePlugin


def initialize():
    PluginManager.register('price_plugin', PricePlugin)
    return {'price_plugin': PricePlugin}
