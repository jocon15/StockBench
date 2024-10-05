from PyQt6.QtWidgets import QFrame, QHBoxLayout
from StockBench.gui.results.base.html_viewer import HTMLViewer
from StockBench.constants import *


class RulesTab(QFrame):
    """Abstract base class for a gui tab."""

    def __init__(self, side):
        super().__init__()
        if side == BUY_SIDE:
            self.chart_key = BUY_RULES_CHART_FILEPATH_KEY
        else:
            self.chart_key = SELL_RULES_CHART_FILEPATH_KEY

        # layout type
        self.layout = QHBoxLayout()

        self.html_viewer = HTMLViewer()

    def render_chart(self, simulation_results):
        self.html_viewer.render_data(simulation_results[self.chart_key])
