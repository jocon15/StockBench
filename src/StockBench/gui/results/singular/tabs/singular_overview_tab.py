from StockBench.gui.results.base.overview_tab import OverviewResultsTab
from StockBench.gui.results.singular.components.sidebar import SingularOverviewSideBar


class SingularOverviewTab(OverviewResultsTab):
    """Tab showing simulation overview for single-symbol simulation results."""
    def __init__(self, progress_observer):
        super().__init__()
        # add shared_components to the layout
        self.results_table = SingularOverviewSideBar(progress_observer)
        self.layout.addWidget(self.results_table)
        self.results_table.setMaximumWidth(300)
        self.layout.addWidget(self.html_viewer)

        # apply the layout
        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        self.render_chart(simulation_results)
        self.results_table.render_data(simulation_results)

    def update_error_message(self, message):
        # pass the error down
        self.results_table.update_error_message(message)
