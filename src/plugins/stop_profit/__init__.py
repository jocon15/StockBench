"""Plugin for the stop profit"""
from .stop_profit import StopProfitPlugin


def initialize():
    return {'stop_profit_plugin': StopProfitPlugin()}
