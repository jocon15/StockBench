from StockBench.gui.results.base.base.simple_vertical_chart_tab import SimpleVerticalChartTab
from StockBench.constants import POSITIONS_PROFIT_LOSS_BAR_CHART_FILEPATH_KEY


class PositionsProfitLossTabVertical(SimpleVerticalChartTab):
    """Abstract base class for a positions analysis tab."""
    CHART_KEY = POSITIONS_PROFIT_LOSS_BAR_CHART_FILEPATH_KEY

    def __init__(self):
        super().__init__()

        self.layout.addWidget(self.html_viewer)

        # apply the layout
        self.setLayout(self.layout)

    def render_chart(self, simulation_results):
        self.html_viewer.render_data(simulation_results[self.CHART_KEY])
