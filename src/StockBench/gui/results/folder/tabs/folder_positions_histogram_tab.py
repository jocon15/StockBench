from StockBench.gui.results.base.base.simple_vertical_chart_tab import SimpleVerticalChartTab
from StockBench.models.constants.chart_filepath_key_constants import POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH_KEY


class FolderPositionsHistogramTabVertical(SimpleVerticalChartTab):
    """Tab for folder position histogram chart.

    Note: Cannot inherit from ResultsTab because
    """

    def __init__(self):
        super().__init__()
        self.layout.addWidget(self.html_viewer)

        self.setLayout(self.layout)

    def render_chart(self, chart_filepaths: dict):
        self.html_viewer.render_data(chart_filepaths[POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH_KEY])
