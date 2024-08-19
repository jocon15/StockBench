from StockBench.gui.results.base.base.result_tab import ResultsTab
from abc import abstractmethod


class OverviewResultsTab(ResultsTab):
    """Abstract base class for a simulation results overview tab."""
    CHART_KEY = 'overview_chart_filepath'

    def __init__(self):
        super().__init__(self.CHART_KEY)

    @abstractmethod
    def render_data(self, simulation_results: dict):
        raise NotImplementedError('You must define an implementation for render_data()!')

    @abstractmethod
    def update_error_message(self, message):
        raise NotImplementedError('You must define an implementation for update_data()!')
