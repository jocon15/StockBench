"""Plugin for volume."""
from .volume import VolumePlugin


def initialize():
    return {'volume_plugin': VolumePlugin()}
