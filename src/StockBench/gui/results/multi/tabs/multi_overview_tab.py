from StockBench.gui.models.simulation_results_bundle import SimulationResultsBundle
from StockBench.gui.results.base.overview_tab import OverviewTabVertical
from StockBench.gui.results.multi.components.multi_sidebar import MultiOverviewSideBar
from StockBench.gui.results.multi.constants.constants import OVERVIEW_CHART_FILEPATH_KEY


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

    def render_data(self, simulation_results_bundle: SimulationResultsBundle):
        self.render_chart(simulation_results_bundle.chart_filepaths)
        self.overview_side_bar.render_data(simulation_results_bundle.simulation_results)

    def render_chart(self, chart_filepaths: dict):
        self.html_viewer.render_data(chart_filepaths[OVERVIEW_CHART_FILEPATH_KEY])

    def update_error_message(self, message):
        # pass the error down
        self.overview_side_bar.update_error_message(message)
