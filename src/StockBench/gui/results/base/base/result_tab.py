from PyQt6.QtWidgets import QFrame, QHBoxLayout
from StockBench.gui.results.base.html_viewer import HTMLViewer


class ResultsTab(QFrame):
    """Abstract base class for a gui tab."""

    def __init__(self, chart_key):
        super().__init__()
        self.chart_key = chart_key

        # layout type
        self.layout = QHBoxLayout()

        self.html_viewer = HTMLViewer()

    def render_chart(self, simulation_results):
        self.html_viewer.render_data(simulation_results[self.chart_key])
