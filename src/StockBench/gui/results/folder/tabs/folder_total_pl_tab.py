from StockBench.gui.results.base.base.simple_vertical_chart_tab import SimpleVerticalChartTab
from StockBench.models.constants.chart_filepath_key_constants import TOTAL_PL_BAR_CHART_FILEPATH_KEY


class FolderTotalProfitLossTabVertical(SimpleVerticalChartTab):
    """Tab for folder total profit loss results chart.

    Note: Cannot inherit from ResultsTab because
    """

    def __init__(self):
        super().__init__()
        self.layout.addWidget(self.html_viewer)

        self.setLayout(self.layout)

    def render_chart(self, chart_filepaths: dict):
        self.html_viewer.render_data(chart_filepaths[TOTAL_PL_BAR_CHART_FILEPATH_KEY])
