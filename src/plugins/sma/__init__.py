"""Plugin for simple moving average."""
from .sma import SMAPlugin


def initialize():
    return {'sma_plugin': SMAPlugin()}
