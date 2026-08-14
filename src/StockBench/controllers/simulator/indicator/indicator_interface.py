from abc import abstractmethod

from StockBench.controllers.simulator.indicator.subplot_interface import SubplotInterface
from StockBench.controllers.simulator.indicator.trigger_interface import TriggerInterface


class IndicatorInterface:
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        # FIXME: validate docstring accuracy
        """Defines the exact name the indicator appears as in a strategy file."""
        raise NotImplementedError('Not implemented yet!')

    @property
    @abstractmethod
    def dataframe_name(self) -> str:
        # FIXME: validate docstring accuracy
        """Defines the exact name the indicator uses in the dataframe."""
        raise NotImplementedError('Not implemented yet!')

    @property
    @abstractmethod
    def trigger(self) -> TriggerInterface:
        # FIXME: validate docstring accuracy
        """The indicator's trigger."""
        raise NotImplementedError('Not implemented yet!')

    @property
    @abstractmethod
    def subplot(self) -> SubplotInterface:
        # FIXME: validate docstring accuracy
        """The indicator's subplot."""
        raise NotImplementedError('Not implemented yet!')
