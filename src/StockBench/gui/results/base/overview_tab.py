from StockBench.gui.models.simulation_results_bundle import SimulationResultsBundle
from StockBench.gui.results.base.base.simple_horizontal_chart_tab import SimpleHorizontalChartTab
from abc import abstractmethod


class OverviewTabVertical(SimpleHorizontalChartTab):
    """Abstract base class for a simulation results overview tab."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def render_data(self, simulation_results_bundle: SimulationResultsBundle):
        raise NotImplementedError('You must define an implementation for render_data()!')

    @abstractmethod
    def update_error_message(self, message):
        raise NotImplementedError('You must define an implementation for update_data()!')
