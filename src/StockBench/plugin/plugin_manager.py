import os
import logging
import importlib
from typing import Any

from StockBench.plugins.candlestick_color.candlestick_color import CandlestickColorPlugin
from StockBench.plugins.ema.ema import EMAPlugin
from StockBench.plugins.price.price import PricePlugin
from StockBench.plugins.rsi.rsi import RSIPlugin
from StockBench.plugins.sma.sma import SMAPlugin
from StockBench.plugins.stochastic.stochastic import StochasticPlugin
from StockBench.plugins.stop_loss.stop_loss import StopLossPlugin
from StockBench.plugins.stop_profit.stop_profit import StopProfitPlugin
from StockBench.plugins.volume.volume import VolumePlugin

log = logging.getLogger()


class PluginManager:

    @staticmethod
    def load_plugins(plugin_dir: str) -> dict:

        # FIXME: plugin dir parameter is deprecated with removal of plugin system

        """Register the plugins here"""

        return {
            'candlestick_color_plugin': CandlestickColorPlugin(),
            'ema_plugin': EMAPlugin(),
            'price_plugin': PricePlugin(),
            'rsi_plugin': RSIPlugin(),
            'sma_plugin': SMAPlugin(),
            'stochastic_plugin': StochasticPlugin(),
            'stop_loss_plugin': StopLossPlugin(),
            'stop_profit_plugin': StopProfitPlugin(),
            'volume_plugin': VolumePlugin()
        }
