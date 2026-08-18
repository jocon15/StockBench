from abc import ABC, abstractmethod

from StockBench.controllers.simulator.indicator.setup_interface import SetupInterface
from StockBench.controllers.simulator.indicator.subplot_interface import SubplotInterface
from StockBench.controllers.simulator.indicator.rule_interface import RuleInterface


class IndicatorInterface(ABC):
    @abstractmethod
    def strategy_name(self) -> str:
        """Defines the exact name the indicator appears as in a strategy file."""
        raise NotImplementedError('Not implemented yet!')

    @abstractmethod
    def dataframe_name(self) -> str:
        """Defines the exact name the indicator uses in the dataframe."""
        raise NotImplementedError('Not implemented yet!')

    @property
    @abstractmethod
    def setup(self) -> SetupInterface:
        """The indicator's setup interface."""
        raise NotImplementedError('Not implemented yet!')

    @property
    @abstractmethod
    def rule(self) -> RuleInterface:
        """The indicator's trigger interface."""
        raise NotImplementedError('Not implemented yet!')

    @property
    @abstractmethod
    def subplot(self) -> SubplotInterface:
        """The indicator's subplot interface."""
        raise NotImplementedError('Not implemented yet!')
