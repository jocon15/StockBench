import logging

log = logging.getLogger()

from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QLabel
from StockBench.gui.windows.overview_tab import OverviewTab, OverviewTable


class MultiOverviewTab(OverviewTab):
    """Widget that houses the simulation results box."""

    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()

        self.results_table = MultiOverviewTable()
        self.layout.addWidget(self.results_table)
        self.results_table.setMaximumWidth(300)
        self.results_table.setMaximumHeight(800)

        self.layout.addWidget(self.webView)

        self.setLayout(self.layout)

    def render_data(self, simulation_results):
        # render the chart
        self.render_chart(simulation_results)
        # render the text box results
        self.results_table.render_data(simulation_results)

    def update_error_message(self, message):
        # pass the error down to the simulation results text box
        self.results_table.update_error_message(message)


class MultiOverviewTable(OverviewTable):
    """Widget that houses the numerical results table."""
    def __init__(self):
        super().__init__()
        # define the layout
        self.layout = QGridLayout()

        # results title
        row = 1
        label = QLabel()
        label.setText('Simulation Results')
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
            self.elapsed_time_data_label.setText(f'{simulation_results["elapsed_time"]} seconds')
            self.trades_made_data_label.setText(f'{simulation_results["trades_made"]}')
            self.effectiveness_data_label.setText(f'{simulation_results["effectiveness"]} %')
            self.total_pl_data_label.setText(f'$ {simulation_results["total_profit_loss"]}')
            self.average_pl_data_label.setText(f'$ {simulation_results["average_profit_loss"]}')
            self.median_pl_data_label.setText(f'$ {simulation_results["median_profit_loss"]}')
            self.stddev_pl_data_label.setText(f'$ {simulation_results["standard_profit_loss_deviation"]}')
        else:
            self.error_message_box.setText(f'Error: {self._error_message}')
