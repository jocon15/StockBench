from StockBench.gui.results.base.sidebar_results_table import SidebarResultsTable
from StockBench.models.constants.simulation_results_constants import *


class MultiResultsSidebarTable(SidebarResultsTable):
    """Widget that houses the numerical results table."""

    def __init__(self):
        super().__init__()
        # trades made label and data label
        row = 1
        self.layout.addWidget(self.trades_made_label, row, 1)
        self.layout.addWidget(self.trades_made_data_label, row, 2)

        # average trade duration label and data label
        row += 1
        self.layout.addWidget(self.average_trade_duration_label, row, 1)
        self.layout.addWidget(self.average_trade_duration_data_label, row, 2)

        # effectiveness label and data label
        row += 1
        self.layout.addWidget(self.effectiveness_label, row, 1)
        self.layout.addWidget(self.effectiveness_data_label, row, 2)

        # total P/L label and data label
        row += 1
        self.layout.addWidget(self.total_pl_label, row, 1)
        self.layout.addWidget(self.total_pl_data_label, row, 2)

        # average P/L label and data label
        row += 1
        self.layout.addWidget(self.average_pl_label, row, 1)
        self.layout.addWidget(self.average_pl_data_label, row, 2)

        # median label and data label
        row += 1
        self.layout.addWidget(self.median_pl_label, row, 1)
        self.layout.addWidget(self.median_pl_data_label, row, 2)

        # stddev label and data label
        row += 1
        self.layout.addWidget(self.stddev_pl_label, row, 1)
        self.layout.addWidget(self.stddev_pl_data_label, row, 2)

        # apply the layout to the frame
        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        if simulation_results.keys():
            self.trades_made_data_label.setText(f'{simulation_results[TRADES_MADE_KEY]}')
            self.average_trade_duration_data_label.setText(f'{simulation_results[AVERAGE_TRADE_DURATION_KEY]:.1f} days')
            self.effectiveness_data_label.setText(f'{simulation_results[EFFECTIVENESS_KEY]:,.2f} %')
            self.total_pl_data_label.setText(f'$ {simulation_results[TOTAL_PL_KEY]:,.2f}')
            self.average_pl_data_label.setText(f'$ {simulation_results[AVERAGE_PL_KEY]:,.2f}')
            self.median_pl_data_label.setText(f'$ {simulation_results[MEDIAN_PL_KEY]:,.2f}')
            self.stddev_pl_data_label.setText(f'$ {simulation_results[STANDARD_PL_DEVIATION_KEY]:,.2f}')
