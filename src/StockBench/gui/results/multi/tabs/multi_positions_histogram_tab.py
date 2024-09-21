from StockBench.charting.multi.multi_charting_engine import MultiChartingEngine
from StockBench.gui.results.base.simple_chart_tab import SimpleChartTab


class MultiPositionsHistogramTab(SimpleChartTab):
    """Tab for multi position histogram chart.

        Note: Cannot inherit from ResultsTab because
        """

    def __init__(self):
        super().__init__()
        # add layouts to widget
        self.layout.addWidget(self.html_viewer)

        # apply the layout
        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        # build the chart
        chart_filepath = MultiChartingEngine.build_positions_histogram_chart(simulation_results)
        # render the chart
        self.html_viewer.render_data(chart_filepath)
