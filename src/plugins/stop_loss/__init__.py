"""Plugin for the stop loss."""
from .stop_loss import StopLossPlugin


def initialize():
    return {'stop_loss_plugin': StopLossPlugin()}
