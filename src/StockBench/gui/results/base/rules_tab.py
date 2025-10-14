from abc import abstractmethod

from PyQt6.QtWidgets import QFrame, QHBoxLayout

from StockBench.charting.charting_engine import ChartingEngine
from StockBench.charting.singular.singular_charting_engine import SingularChartingEngine
from StockBench.gui.results.base.html_viewer import HTMLViewer
from StockBench.constants import *


class RulesTab(QFrame):
    """Abstract base class for a gui tab."""

    def __init__(self, side):
        super().__init__()
        self.side = side

        # layout type
        self.layout = QHBoxLayout()

        self.html_viewer = HTMLViewer()

    @abstractmethod
    def render_chart(self, chart_filepaths: dict):
        raise NotImplementedError('You must define an implementation for render_data()!')
