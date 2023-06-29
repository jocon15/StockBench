"""Plugin for relative strength index."""
from .rsi import RSIPlugin


def initialize():
    return {'rsi_plugin': RSIPlugin()}
