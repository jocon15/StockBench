import logging
from StockBench.controllers.simulator.indicators.candlestick_color.candlestick_color import CandlestickColorIndicator
from StockBench.controllers.simulator.indicators.ema.ema import EMAIndicator
from StockBench.controllers.simulator.indicators.macd.macd import MACDIndicator
from StockBench.controllers.simulator.indicators.price.price import PriceIndicator
from StockBench.controllers.simulator.indicators.rsi.rsi import RSIIndicator
from StockBench.controllers.simulator.indicators.sma.sma import SMAIndicator
from StockBench.controllers.simulator.indicators.stochastic.stochastic import StochasticIndicator
from StockBench.controllers.simulator.indicators.stop_loss.stop_loss import StopLossIndicator
from StockBench.controllers.simulator.indicators.stop_profit.stop_profit import StopProfitIndicator
from StockBench.controllers.simulator.indicators.volume.volume import VolumeIndicator

log = logging.getLogger()


class IndicatorManager:

    @staticmethod
    def load_indicators() -> dict:
        """Register the indicators here."""

        return {
            'candlestick_color_indicator': CandlestickColorIndicator(),
            'ema_indicator': EMAIndicator(),
            'macd_indicator': MACDIndicator(),
            'price_indicator': PriceIndicator(),
            'rsi_indicator': RSIIndicator(),
            'sma_indicator': SMAIndicator(),
            'stochastic_indicator': StochasticIndicator(),
            'stop_loss_indicator': StopLossIndicator(),
            'stop_profit_indicator': StopProfitIndicator(),
            'volume_indicator': VolumeIndicator()
        }
