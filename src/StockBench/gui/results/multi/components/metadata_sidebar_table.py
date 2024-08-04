from PyQt6.QtWidgets import QLabel
from StockBench.gui.results.base.sidebar_results_table import SidebarResultsTable


class MultiMetadataSidebarTable(SidebarResultsTable):
    """Table of overview metadata."""
    def __init__(self):
        super().__init__()
        # strategy label and data label
        row = 1
        self.layout.addWidget(self.strategy_label, row, 1)
        # strategy data label
        self.strategy_data_label = QLabel()
        self.strategy_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(self.strategy_data_label, row, 2)

        # trade-able days label and data label
        row += 1
        self.layout.addWidget(self.trade_able_days_label, row, 1)
        self.layout.addWidget(self.trade_able_days_data_label, row, 2)

        # elapsed time label and data label
        row += 1
        self.layout.addWidget(self.elapsed_time_label, row, 1)
        self.layout.addWidget(self.elapsed_time_data_label, row, 2)

        # apply the layout to the frame
        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        if simulation_results.keys():
            self.strategy_data_label.setText(f'{simulation_results["strategy"]}')
            self.trade_able_days_data_label.setText(f'{simulation_results["trade_able_days"]} days')
            self.elapsed_time_data_label.setText(f'{simulation_results["elapsed_time"]} seconds')
