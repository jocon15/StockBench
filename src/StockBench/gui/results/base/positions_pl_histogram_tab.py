from StockBench.gui.results.base.simple_chart_tab import SimpleChartTab
from StockBench.constants import POSITIONS_PROFIT_LOSS_HISTOGRAM_CHART_FILEPATH_KEY


class PositionsHistogramTab(SimpleChartTab):
    """Tab for singular position histogram chart.

    Note: Cannot inherit from ResultsTab because
    """
    CHART_KEY = POSITIONS_PROFIT_LOSS_HISTOGRAM_CHART_FILEPATH_KEY

    def __init__(self):
        super().__init__()
        # add layouts to widget
        self.layout.addWidget(self.html_viewer)

        # apply the layout
        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        self.html_viewer.render_data(simulation_results[self.CHART_KEY])
