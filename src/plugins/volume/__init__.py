"""Plugin for volume."""
from StockBench.plugin.plugin import PluginManager
from .volume import VolumePlugin


def initialize():
    PluginManager.register('volume_plugin', VolumePlugin)
    return {'volume_plugin': VolumePlugin}
