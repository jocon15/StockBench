from StockBench.gui.results.base.overview_sidebar import OverviewSideBar
from StockBench.gui.results.multi.components.metadata_sidebar_table import MultiMetadataSidebarTable
from StockBench.gui.results.multi.components.results_sidebar_table import MultiResultsSidebarTable
from StockBench.constants import *


class MultiOverviewSideBar(OverviewSideBar):
    """Sidebar that stands next to the overview chart."""
    def __init__(self, progress_observer):
        super().__init__(progress_observer)
        # add shared_components to the layout
        self.layout.addWidget(self.metadata_header)

        self.metadata_table = MultiMetadataSidebarTable()
        self.layout.addWidget(self.metadata_table)

        self.layout.addWidget(self.results_header)

        self.overview_table = MultiResultsSidebarTable()
        self.layout.addWidget(self.overview_table)

        self.layout.addWidget(self.export_json_btn)

        self.layout.addWidget(self.export_excel_btn)

        # pushes the status header and output box to the bottom
        self.layout.addStretch()

        self.layout.addWidget(self.status_header)
        self.layout.addWidget(self.output_box)

        # apply the layout
        self.setLayout(self.layout)

    def render_data(self, simulation_results):
        # save the results to allow exporting
        self.simulation_results_to_export = simulation_results
        # render data in child shared_components
        self.metadata_table.render_data(simulation_results)
        self.overview_table.render_data(simulation_results)

    def _remove_extraneous_info(self, results: dict) -> dict:
        """Remove info from the simulation results that is not relevant to exporting."""
        export_dict = results.copy()

        # remove extraneous data from exported results
        export_dict.pop(ELAPSED_TIME_KEY)
        export_dict.pop(OVERVIEW_CHART_FILEPATH_KEY)
        export_dict.pop(BUY_RULES_CHART_FILEPATH_KEY)
        export_dict.pop(SELL_RULES_CHART_FILEPATH_KEY)
        export_dict.pop(POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY)

        return export_dict
