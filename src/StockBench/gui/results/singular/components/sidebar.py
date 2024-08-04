from StockBench.gui.results.base.overview_sidebar import OverviewSideBar
from StockBench.gui.results.singular.components.metadata_sidebar_table import SingularMetadataSidebarTable
from StockBench.gui.results.singular.components.results_sidebar_table import SingularResultsSidebarTable


class SingularOverviewSideBar(OverviewSideBar):
    """Sidebar that stands next to the overview chart."""
    def __init__(self, progress_observer):
        super().__init__(progress_observer)
        # add shared_components to the layout
        self.layout.addWidget(self.metadata_header)

        self.metadata_table = SingularMetadataSidebarTable()
        self.layout.addWidget(self.metadata_table)

        self.layout.addWidget(self.results_header)

        self.results_table = SingularResultsSidebarTable()
        self.layout.addWidget(self.results_table)

        self.layout.addWidget(self.export_json_btn)

        self.layout.addWidget(self.export_excel_btn)

        # pushes the status header and output box to the bottom
        self.layout.addStretch()

        self.layout.addWidget(self.status_header)
        self.layout.addWidget(self.output_box)

        # apply the layout
        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        # save the results to allow exporting
        self.simulation_results_to_export = simulation_results
        # render data in child shared_components
        self.metadata_table.render_data(simulation_results)
        self.results_table.render_data(simulation_results)

    def _remove_extraneous_info(self, results: dict) -> dict:
        """Remove info from the simulation results that is not relevant to exporting."""
        export_dict = results.copy()

        # remove extraneous data from exported results
        export_dict.pop('symbol')
        export_dict.pop('trade_able_days')
        export_dict.pop('elapsed_time')
        export_dict.pop('buy_rule_analysis_chart_filepath')
        export_dict.pop('sell_rule_analysis_chart_filepath')
        export_dict.pop('position_analysis_chart_filepath')
        export_dict.pop('overview_chart_filepath')

        return export_dict
