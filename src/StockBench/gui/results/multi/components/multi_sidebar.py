from StockBench.controllers.export import MarkdownExporter
from StockBench.gui.results.base.overview_sidebar import OverviewSideBar
from StockBench.gui.results.multi.components.multi_sidebar_metadata_table import MultiMetadataSidebarTable
from StockBench.gui.results.multi.components.multi_sidebar_results_table import MultiResultsSidebarTable
from StockBench.models.constants.general_constants import *


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
        self.layout.addWidget(self.export_md_btn)

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

    def on_export_excel_btn_clicked(self):
        raise NotImplementedError('Singular does not use the export to excel button')

    def on_export_md_btn_clicked(self):
        """Export simulation results to markdown."""
        if self.simulation_results_to_export:
            filepath = MarkdownExporter.export_multi_simulation_to_md(self.simulation_results_to_export)

            # show a message box indicating results were copied
            self._show_message_box('Export Notification', f'Results exported to {filepath}')

    def _remove_extraneous_info(self, results: dict) -> dict:
        """Remove info from the simulation results that is not relevant to exporting."""
        export_dict = results.copy()

        # remove extraneous data from exported results
        export_dict.pop(ELAPSED_TIME_KEY)
        export_dict.pop(OVERVIEW_CHART_FILEPATH_KEY)
        export_dict.pop(BUY_RULES_CHART_FILEPATH_KEY)
        export_dict.pop(SELL_RULES_CHART_FILEPATH_KEY)
        export_dict.pop(POSITIONS_KEY)
        export_dict.pop(POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY)

        return export_dict
