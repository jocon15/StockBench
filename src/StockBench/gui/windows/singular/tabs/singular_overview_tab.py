from PyQt6.QtWidgets import QLabel
from StockBench.gui.windows.base.overview_tab import OverviewTab, OverviewSideBar, OverviewTable


class SingularOverviewTab(OverviewTab):
    """Tab showing simulation overview for single-symbol simulation results."""
    def __init__(self, progress_observer):
        super().__init__()
        # add objects to the layout
        self.results_table = SingularOverviewSideBar(progress_observer)
        self.layout.addWidget(self.results_table)
        self.results_table.setMaximumWidth(230)
        self.results_table.setMaximumHeight(900)
        self.layout.addWidget(self.webView)

        # apply the layout
        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        # render the chart
        self.render_chart(simulation_results)
        # render the text box results
        self.results_table.render_data(simulation_results)

    def update_error_message(self, message):
        # pass the error down to the simulation results text box
        self.results_table.update_error_message(message)


class SingularOverviewSideBar(OverviewSideBar):
    def __init__(self, progress_observer):
        super().__init__(progress_observer)
        # add objects to the layout
        metadata_label = QLabel()
        metadata_label.setText('Metadata')
        metadata_label.setStyleSheet(self.title_stylesheet)
        self.layout.addWidget(metadata_label)

        self.metadata_table = SingularMetadataOverviewTable()
        self.layout.addWidget(self.metadata_table)

        results_label = QLabel()
        results_label.setText("Simulation Results")
        results_label.setStyleSheet(self.title_stylesheet)
        self.layout.addWidget(results_label)

        self.results_table = SingularResultsOverviewTable()
        self.layout.addWidget(self.results_table)

        # pushes the status title and output box to the bottom
        self.layout.addStretch()

        self.layout.addWidget(self.status_title)
        self.layout.addWidget(self.output_box)

        # apply the layout
        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        self.metadata_table.render_data(simulation_results)
        self.results_table.render_data(simulation_results)


class SingularMetadataOverviewTable(OverviewTable):
    def __init__(self):
        super().__init__()
        # symbol title
        row = 1
        label = QLabel()
        label.setText('Symbol')
        label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(label, row, 1)
        # elapsed time data label
        self.symbol_data_label = QLabel()
        self.symbol_data_label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(self.symbol_data_label, row, 2)

        # trade-able days title
        row += 1
        label = QLabel()
        label.setText('Length')
        label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(label, row, 1)
        # elapsed time data label
        self.trade_able_days_data_label = QLabel()
        self.trade_able_days_data_label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(self.trade_able_days_data_label, row, 2)

        # apply the layout to the frame
        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        if simulation_results.keys():
            self.symbol_data_label.setText(f'{simulation_results["symbol"]}')
            self.trade_able_days_data_label.setText(f'{simulation_results["trade_able_days"]} days')


class SingularResultsOverviewTable(OverviewTable):
    """Widget for numeric overview data."""
    def __init__(self):
        super().__init__()
        # elapsed time title
        row = 1
        label = QLabel()
        label.setText('Elapsed Time')
        label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(label, row, 1)
        # elapsed time data label
        self.elapsed_time_data_label = QLabel()
        self.elapsed_time_data_label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(self.elapsed_time_data_label, row, 2)

        # trades made title
        label = QLabel()
        label.setText('Trades Made')
        label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(label, row, 1)
        # trades made data label
        self.trades_made_data_label = QLabel()
        self.trades_made_data_label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(self.trades_made_data_label, row, 2)

        # effectiveness title
        row += 1
        label = QLabel()
        label.setText('Effectiveness')
        label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(label, row, 1)
        # effectiveness data label
        self.effectiveness_data_label = QLabel()
        self.effectiveness_data_label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(self.effectiveness_data_label, row, 2)

        # total P/L title
        row += 1
        label = QLabel()
        label.setText('Total P/L')
        label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(label, row, 1)
        # total P/L data label
        self.total_pl_data_label = QLabel()
        self.total_pl_data_label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(self.total_pl_data_label, row, 2)

        # average P/L title
        row += 1
        label = QLabel()
        label.setText('Average P/L')
        label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(label, row, 1)
        # average P/L data
        self.average_pl_data_label = QLabel()
        self.average_pl_data_label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(self.average_pl_data_label, row, 2)

        # median title
        row += 1
        label = QLabel()
        label.setText('Median P/L')
        label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(label, row, 1)
        # median data label
        self.median_pl_data_label = QLabel()
        self.median_pl_data_label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(self.median_pl_data_label, row, 2)

        # stddev title
        row += 1
        label = QLabel()
        label.setText('Stddev P/L')
        label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(label, row, 1)
        # stddev data label
        self.stddev_pl_data_label = QLabel()
        self.stddev_pl_data_label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(self.stddev_pl_data_label, row, 2)

        # account value title
        row += 1
        label = QLabel()
        label.setText('Account Value')
        label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(label, row, 1)
        # account value data label
        self.account_value_data_label = QLabel()
        self.account_value_data_label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(self.account_value_data_label, row, 2)

        # stretch the row and column to show natural size
        # self.layout.setRowStretch(self.layout.rowCount(), 1)
        # self.layout.setColumnStretch(self.layout.columnCount(), 1)

        # apply the layout to the frame
        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        if simulation_results.keys():
            self.elapsed_time_data_label.setText(f'{simulation_results["elapsed_time"]} seconds')
            self.trades_made_data_label.setText(f'{simulation_results["trades_made"]}')
            self.effectiveness_data_label.setText(f'{simulation_results["effectiveness"]} %')
            self.total_pl_data_label.setText(f'$ {simulation_results["total_profit_loss"]}')
            self.average_pl_data_label.setText(f'$ {simulation_results["average_profit_loss"]}')
            self.median_pl_data_label.setText(f'$ {simulation_results["median_profit_loss"]}')
            self.stddev_pl_data_label.setText(f'$ {simulation_results["standard_profit_loss_deviation"]}')
            self.account_value_data_label.setText(f'$ {simulation_results["account_value"]}')
