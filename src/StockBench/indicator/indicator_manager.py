import logging
from StockBench.indicators.candlestick_color.candlestick_color import CandlestickColorIndicator
from StockBench.indicators.ema.ema import EMAIndicator
from StockBench.indicators.price.price import PriceIndicator
from StockBench.indicators.rsi.rsi import RSIIndicator
from StockBench.indicators.sma.sma import SMAIndicator
from StockBench.indicators.stochastic.stochastic import StochasticIndicator
from StockBench.indicators.stop_loss.stop_loss import StopLossIndicator
from StockBench.indicators.stop_profit.stop_profit import StopProfitIndicator
from StockBench.indicators.volume.volume import VolumeIndicator

log = logging.getLogger()


class IndicatorManager:

    @staticmethod
    def load_indicators() -> dict:
        """Register the indicators here"""

        return {
            'candlestick_color_indicator': CandlestickColorIndicator(),
            'ema_indicator': EMAIndicator(),
            'price_indicator': PriceIndicator(),
            'rsi_indicator': RSIIndicator(),
            'sma_indicator': SMAIndicator(),
            'stochastic_indicator': StochasticIndicator(),
            'stop_loss_indicator': StopLossIndicator(),
            'stop_profit_indicator': StopProfitIndicator(),
            'volume_indicator': VolumeIndicator()
        }
