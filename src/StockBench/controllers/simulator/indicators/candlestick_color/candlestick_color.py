from .setup import CandleStickSetup
from .trigger import CandlestickColorRule
from StockBench.controllers.simulator.indicator.indicator_interface import IndicatorInterface
from StockBench.controllers.simulator.indicator.setup_interface import SetupInterface
from StockBench.controllers.simulator.indicator.rule_interface import RuleInterface


class CandlestickColorIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_symbol = 'color'
        self.__data_name = self.__strategy_symbol
        self.__setup = CandleStickSetup(self.__strategy_symbol)
        self.__trigger = CandlestickColorRule(self.__strategy_symbol)

    def strategy_name(self) -> str:
        return self.__strategy_symbol

    def dataframe_name(self) -> str:
        return self.__data_name

    @property
    def setup(self) -> SetupInterface:
        return self.__setup

    @property
    def trigger(self) -> RuleInterface:
        return self.__trigger

    @property
    def subplot(self):
        # note: candlestick colors do not have a subplot
        return None
