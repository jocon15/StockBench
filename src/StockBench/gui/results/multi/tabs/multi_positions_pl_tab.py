from StockBench.gui.results.base.base.simple_vertical_chart_tab import SimpleVerticalChartTab
from StockBench.gui.results.multi.constants.constants import POSITIONS_PL_BAR_CHART_FILEPATH_KEY


class MultiPositionsProfitLossTabVertical(SimpleVerticalChartTab):
    """Generic positions analysis tab."""

    def __init__(self):
        super().__init__()

        self.layout.addWidget(self.html_viewer)

        self.setLayout(self.layout)

    def render_chart(self, chart_filepaths):
        self.html_viewer.render_data(chart_filepaths[POSITIONS_PL_BAR_CHART_FILEPATH_KEY])
