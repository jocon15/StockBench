from StockBench.gui.results.base.sidebar_results_table import SidebarResultsTable
from StockBench.models.constants.simulation_results_constants import *


class MultiResultsSidebarTable(SidebarResultsTable):
    """Widget that houses the numerical results table."""

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
        self.layout.addWidget(self.spacer, row, 1)

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
        self.layout.addWidget(self.spacer, row, 1)

        row += 1
        self.layout.addWidget(self.average_plpc_label, row, 1)
        self.layout.addWidget(self.average_plpc_data_label, row, 2)

        row += 1
        self.layout.addWidget(self.median_plpc_label, row, 1)
        self.layout.addWidget(self.median_plpc_data_label, row, 2)

        row += 1
        self.layout.addWidget(self.stddev_plpc_label, row, 1)
        self.layout.addWidget(self.stddev_plpc_data_label, row, 2)

        row += 1
        self.layout.addWidget(self.spacer, row, 1)

        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        if simulation_results.keys():
            self.trades_made_data_label.setText(f'{simulation_results[TRADES_MADE_KEY]}')
            self.average_trade_duration_data_label.setText(f'{simulation_results[AVERAGE_TRADE_DURATION_KEY]:.1f} days')
            self.effectiveness_data_label.setText(f'{simulation_results[EFFECTIVENESS_KEY]:,.2f} %')
            self.total_pl_data_label.setText(f'$ {simulation_results[TOTAL_PL_KEY]:,.2f}')
            self.average_pl_data_label.setText(f'$ {simulation_results[AVERAGE_PL_KEY]:,.2f}')
            self.median_pl_data_label.setText(f'$ {simulation_results[MEDIAN_PL_KEY]:,.2f}')
            self.stddev_pl_data_label.setText(f'$ {simulation_results[STANDARD_DEVIATION_PL_KEY]:,.2f}')
            self.average_plpc_data_label.setText(f'{simulation_results[AVERAGE_PLPC_KEY]:,.2f} %')
            self.median_plpc_data_label.setText(f'{simulation_results[MEDIAN_PLPC_KEY]:,.2f} %')
            self.stddev_plpc_data_label.setText(f'{simulation_results[STANDARD_DEVIATION_PLPC_KEY]:,.2f} %')
