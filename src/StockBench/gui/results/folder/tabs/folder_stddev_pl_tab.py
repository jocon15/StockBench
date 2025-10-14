from StockBench.gui.results.base.base.simple_vertical_chart_tab import SimpleVerticalChartTab
from StockBench.gui.results.folder.constants.constants import STDDEV_PL_BAR_CHART_FILEPATH_KEY


class FolderStandardDeviationProfitLossTabVertical(SimpleVerticalChartTab):
    """Tab for folder standard deviation results chart.

    Note: Cannot inherit from ResultsTab because
    """

    def __init__(self):
        super().__init__()
        self.layout.addWidget(self.html_viewer)

        self.setLayout(self.layout)

    def render_chart(self, chart_filepaths: dict):
        self.html_viewer.render_data(chart_filepaths[STDDEV_PL_BAR_CHART_FILEPATH_KEY])
