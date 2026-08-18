from StockBench.controllers.simulator.indicator.indicator_interface import IndicatorInterface
from .setup import StochasticSetup
from .subplot import StochasticSubplot
from .rule import StochasticRule


class StochasticIndicator(IndicatorInterface):
    def __init__(self):
        self.__strategy_symbol = 'stochastic'
        self.__data_name = self.__strategy_symbol
        self.__setup = StochasticSetup(self.__strategy_symbol)
        self.__trigger = StochasticRule(self.__strategy_symbol)
        self.__subplot = StochasticSubplot()

    def strategy_name(self) -> str:
        return self.__strategy_symbol

    def dataframe_name(self) -> str:
        return self.__data_name

    @property
    def setup(self) -> StochasticSetup:
        return self.__setup

    @property
    def rule(self) -> StochasticRule:
        return self.__trigger

    @property
    def subplot(self) -> StochasticSubplot:
        return self.__subplot
