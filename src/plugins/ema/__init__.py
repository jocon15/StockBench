"""Plugin for exponential moving average."""
from .ema import EMAPlugin


def initialize():
    return {'ema_plugin': EMAPlugin()}
