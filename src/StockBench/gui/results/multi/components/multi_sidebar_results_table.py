from StockBench.gui.results.base.sidebar_results_table import SidebarResultsTable


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

            self.trades_made_data_label.setText(f'{simulation_results["trades_made"]}')
            self.average_trade_duration_data_label.setText(f'{simulation_results["average_trade_duration"]} days')
            self.effectiveness_data_label.setText(f'{simulation_results["effectiveness"]} %')
            self.total_pl_data_label.setText(f'$ {simulation_results["total_profit_loss"]}')
            self.average_pl_data_label.setText(f'$ {simulation_results["average_profit_loss"]}')
            self.median_pl_data_label.setText(f'$ {simulation_results["median_profit_loss"]}')
            self.stddev_pl_data_label.setText(f'$ {simulation_results["standard_profit_loss_deviation"]}')
