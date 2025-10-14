from abc import abstractmethod
from PyQt6.QtWidgets import QFrame, QHBoxLayout

from StockBench.gui.models.simulation_results_bundle import SimulationResultsBundle
from StockBench.gui.results.base.html_viewer import HTMLViewer


class SimpleHorizontalChartTab(QFrame):
    """Does not inherit from ResultsFrame because ResultsFrame uses chart key. This class does not use
    chart key and will be building the chart itself. This is because the charts used here are not produced
    by the simulator due to the nature of the simulator and its inability to create charts for a folder run."""
    def __init__(self):
        super().__init__()
        # layout type
        self.layout = QHBoxLayout()

        self.html_viewer = HTMLViewer()

    @abstractmethod
    def render_chart(self, chart_filepaths: dict):
        raise NotImplementedError('You must define an implementation for render_data()!')
