"""Plugin for price."""
from .price import PricePlugin


def initialize():
    return {'price_plugin': PricePlugin()}
