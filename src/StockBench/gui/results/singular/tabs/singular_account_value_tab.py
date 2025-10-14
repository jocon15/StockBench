from StockBench.gui.results.base.base.simple_vertical_chart_tab import SimpleVerticalChartTab
from StockBench.gui.results.singular.constants.constants import ACCOUNT_VALUE_LINE_CHART_FILEPATH


class SingularAccountValueTabVertical(SimpleVerticalChartTab):
    """Account value over time chart tab."""

    def __init__(self):
        super().__init__()

        self.layout.addWidget(self.html_viewer)

        self.setLayout(self.layout)

    def render_chart(self, chart_filepaths: dict):
        self.html_viewer.render_data(chart_filepaths[ACCOUNT_VALUE_LINE_CHART_FILEPATH])
