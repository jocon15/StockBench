from StockBench.gui.results.base.base.simple_vertical_chart_tab import SimpleVerticalChartTab
from StockBench.constants import ACCOUNT_VALUE_BAR_CHART_FILEPATH


class SingularAccountValueTabVertical(SimpleVerticalChartTab):
    """Account value over time chart tab."""
    CHART_KEY = ACCOUNT_VALUE_BAR_CHART_FILEPATH

    def __init__(self):
        super().__init__()

        self.layout.addWidget(self.html_viewer)

        # apply the layout
        self.setLayout(self.layout)

    def render_chart(self, simulation_results):
        self.html_viewer.render_data(simulation_results[self.CHART_KEY])
