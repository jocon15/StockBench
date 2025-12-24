from PyQt6.QtWidgets import QLabel
from StockBench.gui.results.base.sidebar_results_table import SidebarResultsTable
from StockBench.models.constants.simulation_results_constants import *


class FolderMetadataSidebarTable(SidebarResultsTable):
    """Table of overview metadata."""
    def __init__(self):
        super().__init__()
        row = 1
        self.layout.addWidget(self.trade_able_days_label, row, 1)
        self.layout.addWidget(self.trade_able_days_data_label, row, 2)

        row += 1
        self.layout.addWidget(self.elapsed_time_label, row, 1)
        self.layout.addWidget(self.elapsed_time_data_label, row, 2)

        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        if simulation_results.keys():
            self.trade_able_days_data_label.setText(f'{simulation_results[TRADE_ABLE_DAYS_KEY]} days')
            self.elapsed_time_data_label.setText(f'{simulation_results[ELAPSED_TIME_KEY]:,.2f} seconds')
