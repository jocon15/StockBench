from StockBench.gui.models.simulation_results_bundle import SimulationResultsBundle
from StockBench.gui.results.base.overview_tab import OverviewTabVertical
from StockBench.gui.results.singular.components.singular_sidebar import SingularOverviewSideBar
from StockBench.models.constants.chart_filepath_key_constants import OVERVIEW_CHART_FILEPATH_KEY


class SingularOverviewTab(OverviewTabVertical):
    """Tab showing simulation overview for single-symbol simulation results."""
    def __init__(self, progress_observer, show_volume: bool):
        super().__init__()
        self.show_volume = show_volume

        self.results_table = SingularOverviewSideBar(progress_observer)
        self.layout.addWidget(self.results_table)
        self.results_table.setMaximumWidth(300)
        self.layout.addWidget(self.html_viewer)

        self.setLayout(self.layout)

    def render_data(self, simulation_results_bundle: SimulationResultsBundle):
        self.render_chart(simulation_results_bundle.chart_filepaths)
        self.results_table.render_data(simulation_results_bundle.simulation_results)

    def render_chart(self, chart_filepaths: dict):
        self.html_viewer.render_data(chart_filepaths[OVERVIEW_CHART_FILEPATH_KEY])

    def update_error_message(self, message):
        # pass the error down
        self.results_table.update_error_message(message)
