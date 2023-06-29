"""Plugin for the stochastic oscillator"""
from .stochastic import StochasticPlugin


def initialize():
    return {'stochastic_plugin': StochasticPlugin()}
