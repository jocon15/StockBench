from StockBench.gui.results.base.base.rules_tab import RulesTab
from StockBench.constants import OVERVIEW_CHART_FILEPATH_KEY
from abc import abstractmethod


class OverviewTab(RulesTab):
    """Abstract base class for a simulation results overview tab."""
    CHART_KEY = OVERVIEW_CHART_FILEPATH_KEY

    def __init__(self):
        super().__init__(self.CHART_KEY)

    @abstractmethod
    def render_data(self, simulation_results: dict):
        raise NotImplementedError('You must define an implementation for render_data()!')

    @abstractmethod
    def update_error_message(self, message):
        raise NotImplementedError('You must define an implementation for update_data()!')
