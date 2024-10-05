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

        # apply the layout
        self.setLayout(self.layout)

    def render_data(self, simulation_results):
        self.overview_side_bar.render_data(simulation_results)
        self.results_table.render_data(simulation_results)

    def update_error_message(self, message):
        # pass the error down
        self.overview_side_bar.update_error_message(message)
