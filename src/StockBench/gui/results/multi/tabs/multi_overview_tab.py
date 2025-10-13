from StockBench.charting.charting_engine import ChartingEngine
from StockBench.charting.multi.multi_charting_engine import MultiChartingEngine
from StockBench.constants import INITIAL_ACCOUNT_VALUE_KEY, MULTI_RESULTS_KEY
from StockBench.gui.results.base.overview_tab import OverviewTabVertical
from StockBench.gui.results.multi.components.multi_sidebar import MultiOverviewSideBar


class MultiOverviewTab(OverviewTabVertical):
    """Tab showing simulation overview for multi-symbol simulation results."""

    def __init__(self, progress_observer):
        super().__init__()
        # add shared_components to the layout
        self.overview_side_bar = MultiOverviewSideBar(progress_observer)
        self.layout.addWidget(self.overview_side_bar)
        self.overview_side_bar.setMaximumWidth(300)
        self.layout.addWidget(self.html_viewer)

        self.setLayout(self.layout)

    def render_data(self, simulation_results):
        self.render_chart(simulation_results)
        self.overview_side_bar.render_data(simulation_results)

    def render_chart(self, simulation_results: dict):
        chart_filepath = MultiChartingEngine.build_multi_overview_chart(
            simulation_results[MULTI_RESULTS_KEY],
            simulation_results[INITIAL_ACCOUNT_VALUE_KEY],
            ChartingEngine.TEMP_SAVE)

        self.html_viewer.render_data(chart_filepath)

    def update_error_message(self, message):
        # pass the error down
        self.overview_side_bar.update_error_message(message)
