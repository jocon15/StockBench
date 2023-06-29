"""Plugin for candlestick colors."""
from .candlestick_color import CandlestickColorPlugin


def initialize():
    return {'candlestick_color_plugin': CandlestickColorPlugin()}

