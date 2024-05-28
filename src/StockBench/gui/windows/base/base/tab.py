from PyQt6.QtWidgets import QFrame, QHBoxLayout
from StockBench.gui.windows.base.html_viewer import HTMLViewer


class Tab(QFrame):
    """Abstract base class for a gui tab."""

    def __init__(self, chart_key):
        super().__init__()
        # layout type
        self.layout = QHBoxLayout()

        self.html_viewer = HTMLViewer(chart_key)

    def render_chart(self, simulation_results):
        self.html_viewer.render_chart(simulation_results)
