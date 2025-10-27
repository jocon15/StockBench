from StockBench.gui.models.simulation_results_bundle import SimulationResult
from StockBench.gui.results.base.overview_tab import OverviewTabVertical
from StockBench.gui.results.folder.components.folder_sidebar import FolderOverviewSidebar
from StockBench.gui.results.folder.components.folder_results_table import FolderResultsTable


class FolderOverViewTab(OverviewTabVertical):
    def __init__(self, strategies, progress_observers):
        super().__init__()
        self.overview_side_bar = FolderOverviewSidebar(progress_observers)
        self.layout.addWidget(self.overview_side_bar)
        self.overview_side_bar.setMaximumWidth(300)

        self.results_table = FolderResultsTable(strategies)
        self.layout.addWidget(self.results_table)

        self.setLayout(self.layout)

    def render_data(self, simulation_results_bundle: SimulationResult):
        self.overview_side_bar.render_data(simulation_results_bundle.simulation_results)
        self.results_table.render_data(simulation_results_bundle.simulation_results)

    def render_chart(self, chart_filepaths: dict):
        # Since folder overview tab has a table instead of a chart, this method is unused. It is an abstract method
        # in the super class, so it must be implemented. Hence, the exception
        raise NotImplementedError("Not implemented")

    def update_error_message(self, message):
        # pass the error down
        self.overview_side_bar.update_error_message(message)
