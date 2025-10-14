from StockBench.gui.results.base.base.simple_vertical_chart_tab import SimpleVerticalChartTab
from StockBench.gui.results.folder.constants.constants import EFFECTIVENESS_BAR_CHART_FILEPATH_KEY


class FolderEffectivenessTabVertical(SimpleVerticalChartTab):
    """Tab for folder effectiveness results chart.

    Note: Cannot inherit from ResultsTab because
    """

    def __init__(self):
        super().__init__()
        self.layout.addWidget(self.html_viewer)

        self.setLayout(self.layout)

    def render_chart(self, chart_filepaths: dict):
        self.html_viewer.render_data(chart_filepaths[EFFECTIVENESS_BAR_CHART_FILEPATH_KEY])
