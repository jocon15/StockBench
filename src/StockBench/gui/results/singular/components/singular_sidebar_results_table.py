from PyQt6.QtWidgets import QLabel

from StockBench.gui.results.base.sidebar_results_table import SidebarResultsTable
from StockBench.models.constants.simulation_results_constants import *


class SingularResultsSidebarTable(SidebarResultsTable):
    """Table of overview results data."""
    def __init__(self):
        super().__init__()
        row = 1
        self.layout.addWidget(self.trades_made_label, row, 1)
        self.layout.addWidget(self.trades_made_data_label, row, 2)

        row += 1
        self.layout.addWidget(self.average_trade_duration_label, row, 1)
        self.layout.addWidget(self.average_trade_duration_data_label, row, 2)

        row += 1
        self.layout.addWidget(self.effectiveness_label, row, 1)
        self.layout.addWidget(self.effectiveness_data_label, row, 2)

        row += 1
        self.layout.addWidget(self.total_pl_label, row, 1)
        self.layout.addWidget(self.total_pl_data_label, row, 2)

        row += 1
        self.layout.addWidget(self.average_pl_label, row, 1)
        self.layout.addWidget(self.average_pl_data_label, row, 2)

        row += 1
        self.layout.addWidget(self.median_pl_label, row, 1)
        self.layout.addWidget(self.median_pl_data_label, row, 2)

        row += 1
        self.layout.addWidget(self.stddev_pl_label, row, 1)
        self.layout.addWidget(self.stddev_pl_data_label, row, 2)

        row += 1
        label = QLabel()
        label.setText('Account Value')
        label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(label, row, 1)

        self.account_value_data_label = QLabel()
        self.account_value_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(self.account_value_data_label, row, 2)

        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        if simulation_results.keys():
            self.elapsed_time_data_label.setText(f'{simulation_results[ELAPSED_TIME_KEY]:.2f} seconds')
            self.trades_made_data_label.setText(f'{simulation_results[TRADES_MADE_KEY]}')
            self.average_trade_duration_data_label.setText(f'{simulation_results[AVERAGE_TRADE_DURATION_KEY]:.1f} days')
            self.effectiveness_data_label.setText(f'{simulation_results[EFFECTIVENESS_KEY]:,.2f} %')
            self.total_pl_data_label.setText(f'$ {simulation_results[TOTAL_PL_KEY]:,.2f}')
            self.average_pl_data_label.setText(f'$ {simulation_results[AVERAGE_PL_KEY]:,.2f}')
            self.median_pl_data_label.setText(f'$ {simulation_results[MEDIAN_PL_KEY]:,.2f}')
            self.stddev_pl_data_label.setText(f'$ {simulation_results[STANDARD_DEVIATION_PL_KEY]:,.2f}')
            self.account_value_data_label.setText(f'$ {simulation_results[FINAL_ACCOUNT_VALUE_KEY]:,.2f}')
