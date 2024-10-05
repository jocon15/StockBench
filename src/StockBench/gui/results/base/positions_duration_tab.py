from abc import ABC
from StockBench.gui.results.base.simple_chart_tab import SimpleChartTab
from StockBench.constants import POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY


class PositionsDurationTab(SimpleChartTab):
    """Abstract base class for a positions analysis tab."""
    CHART_KEY = POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY

    def __init__(self):
        super().__init__()

        self.layout.addWidget(self.html_viewer)

        # apply the layout
        self.setLayout(self.layout)

    def render_chart(self, simulation_results):
        self.html_viewer.render_data(simulation_results[self.CHART_KEY])
