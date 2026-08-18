from .setup import CandleStickSetup
from .trigger import CandlestickColorTrigger
from StockBench.controllers.simulator.indicator.indicator_interface import IndicatorInterface
from StockBench.controllers.simulator.indicator.setup_interface import SetupInterface
from StockBench.controllers.simulator.indicator.trigger_interface import TriggerInterface


class CandlestickColorIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_symbol = 'color'
        self.__data_name = self.__strategy_symbol
        self.__setup = CandleStickSetup(self.__strategy_symbol)
        self.__trigger = CandlestickColorTrigger(self.__strategy_symbol)

    def strategy_name(self) -> str:
        return self.__strategy_symbol

    def dataframe_name(self) -> str:
        return self.__data_name

    @property
    def setup(self) -> SetupInterface:
        return self.__setup

    def trigger(self) -> TriggerInterface:
        return self.__trigger

    def subplot(self):
        # note: candlestick colors do not have a subplot
        return None
