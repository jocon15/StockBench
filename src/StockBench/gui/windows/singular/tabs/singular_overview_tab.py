from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QLabel
from StockBench.gui.windows.base.overview_tab import OverviewTab, OverviewTable


class SingularOverviewTab(OverviewTab):
    """Tab showing simulation overview for single-symbol simulation results."""
    def __init__(self):
        super().__init__()
        # add objects to the layout
        self.results_table = SingularOverviewTable()
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


class SingularOverviewTable(OverviewTable):
    """Widget for numeric overview data."""
    def __init__(self):
        super().__init__()
        # define the layout
        self.layout = QGridLayout()

        # parameters title
        row = 1
        label = QLabel()
        label.setText('Metadata')
        label.setStyleSheet(self.title_stylesheet)
        self.layout.addWidget(label, row, 1)

        # symbol title
        row += 1
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

        # results title
        row += 1
        label = QLabel()
        label.setText('Results')
        label.setStyleSheet(self.title_stylesheet)
        self.layout.addWidget(label, row, 1)

        # elapsed time title
        row += 1
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

        # error data label
        row += 1
        self.layout.addWidget(self.error_message_box, row, 1)

        # stretch the row and column to show natural size
        self.layout.setRowStretch(self.layout.rowCount(), 1)
        self.layout.setColumnStretch(self.layout.columnCount(), 1)

        # apply the layout to the frame
        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        if not self._error_message:
            self.symbol_data_label.setText(f'{simulation_results["symbol"]}')
            self.trade_able_days_data_label.setText(f'{simulation_results["trade_able_days"]} days')
            self.elapsed_time_data_label.setText(f'{simulation_results["elapsed_time"]} seconds')
            self.trades_made_data_label.setText(f'{simulation_results["trades_made"]}')
            self.effectiveness_data_label.setText(f'{simulation_results["effectiveness"]} %')
            self.total_pl_data_label.setText(f'$ {simulation_results["total_profit_loss"]}')
            self.average_pl_data_label.setText(f'$ {simulation_results["average_profit_loss"]}')
            self.median_pl_data_label.setText(f'$ {simulation_results["median_profit_loss"]}')
            self.stddev_pl_data_label.setText(f'$ {simulation_results["standard_profit_loss_deviation"]}')
            self.account_value_data_label.setText(f'$ {simulation_results["account_value"]}')
        else:
            self.error_message_box.setText(f'Error: {self._error_message}')
