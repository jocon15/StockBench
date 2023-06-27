"""Plugin for the stochastic oscillator"""
from StockBench.plugin.plugin import PluginManager
from .stochastic import StochasticPlugin


def initialize():
    PluginManager.register('stochastic_plugin', StochasticPlugin)
    return {'stochastic_plugin': StochasticPlugin}
