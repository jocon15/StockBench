from StockBench.charting.folder.folder_charting_engine import FolderChartingEngine
from StockBench.gui.results.base.base.simple_chart_tab import SimpleChartTab


class FolderMedianProfitLossTab(SimpleChartTab):
    """Tab for folder effectiveness results chart.

    Note: Cannot inherit from ResultsTab because
    """
    def __init__(self):
        super().__init__()
        # add layouts to widget
        self.layout.addWidget(self.html_viewer)

        # apply the layout
        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        # normalize the results
        results = simulation_results['results']
        # build the chart
        chart_filepath = FolderChartingEngine.build_median_pl_chart(results)
        # render the chart
        self.html_viewer.render_data(chart_filepath)
