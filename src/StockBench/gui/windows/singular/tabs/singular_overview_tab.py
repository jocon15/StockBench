from PyQt6.QtWidgets import QLabel
from StockBench.gui.windows.base.overview_tab import OverviewTab, OverviewSideBar, OverviewTable


class SingularOverviewTab(OverviewTab):
    """Tab showing simulation overview for single-symbol simulation results."""
    def __init__(self, progress_observer):
        super().__init__()
        # add objects to the layout
        self.results_table = SingularOverviewSideBar(progress_observer)
        self.layout.addWidget(self.results_table)
        self.results_table.setMaximumWidth(300)
        self.layout.addWidget(self.html_viewer)

        # apply the layout
        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        self.render_chart(simulation_results)
        self.results_table.render_data(simulation_results)

    def update_error_message(self, message):
        # pass the error down
        self.results_table.update_error_message(message)


class SingularOverviewSideBar(OverviewSideBar):
    """Sidebar that stands next to the overview chart."""
    def __init__(self, progress_observer):
        super().__init__(progress_observer)
        # add objects to the layout
        metadata_header = QLabel()
        metadata_header.setText('Metadata')
        metadata_header.setStyleSheet(self.HEADER_STYLESHEET)
        self.layout.addWidget(metadata_header)

        self.metadata_table = SingularMetadataOverviewTable()
        self.layout.addWidget(self.metadata_table)

        self.layout.addWidget(self.results_header)

        self.results_table = SingularResultsOverviewTable()
        self.layout.addWidget(self.results_table)

        # pushes the status header and output box to the bottom
        self.layout.addStretch()

        self.layout.addWidget(self.status_header)
        self.layout.addWidget(self.output_box)

        # apply the layout
        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        self.metadata_table.render_data(simulation_results)
        self.results_table.render_data(simulation_results)


class SingularMetadataOverviewTable(OverviewTable):
    """Table of overview metadata."""
    def __init__(self):
        super().__init__()
        # symbol header
        row = 1
        label = QLabel()
        label.setText('Symbol')
        label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(label, row, 1)
        # elapsed time data label
        self.symbol_data_label = QLabel()
        self.symbol_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(self.symbol_data_label, row, 2)

        # trade-able days header
        row += 1
        label = QLabel()
        label.setText('Length')
        label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(label, row, 1)
        # elapsed time data label
        self.trade_able_days_data_label = QLabel()
        self.trade_able_days_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(self.trade_able_days_data_label, row, 2)

        # apply the layout to the frame
        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        if simulation_results.keys():
            self.symbol_data_label.setText(f'{simulation_results["symbol"]}')
            self.trade_able_days_data_label.setText(f'{simulation_results["trade_able_days"]} days')


class SingularResultsOverviewTable(OverviewTable):
    """Table of overview results data."""
    def __init__(self):
        super().__init__()
        # elapsed time header
        row = 1
        label = QLabel()
        label.setText('Elapsed Time')
        label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(label, row, 1)
        # elapsed time data label
        self.elapsed_time_data_label = QLabel()
        self.elapsed_time_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(self.elapsed_time_data_label, row, 2)

        # trades made header
        label = QLabel()
        label.setText('Trades Made')
        label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(label, row, 1)
        # trades made data label
        self.trades_made_data_label = QLabel()
        self.trades_made_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(self.trades_made_data_label, row, 2)

        # effectiveness header
        row += 1
        label = QLabel()
        label.setText('Effectiveness')
        label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(label, row, 1)
        # effectiveness data label
        self.effectiveness_data_label = QLabel()
        self.effectiveness_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(self.effectiveness_data_label, row, 2)

        # total P/L header
        row += 1
        label = QLabel()
        label.setText('Total P/L')
        label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(label, row, 1)
        # total P/L data label
        self.total_pl_data_label = QLabel()
        self.total_pl_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(self.total_pl_data_label, row, 2)

        # average P/L header
        row += 1
        label = QLabel()
        label.setText('Average P/L')
        label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(label, row, 1)
        # average P/L data
        self.average_pl_data_label = QLabel()
        self.average_pl_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(self.average_pl_data_label, row, 2)

        # median header
        row += 1
        label = QLabel()
        label.setText('Median P/L')
        label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(label, row, 1)
        # median data label
        self.median_pl_data_label = QLabel()
        self.median_pl_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(self.median_pl_data_label, row, 2)

        # stddev header
        row += 1
        label = QLabel()
        label.setText('Stddev P/L')
        label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(label, row, 1)
        # stddev data label
        self.stddev_pl_data_label = QLabel()
        self.stddev_pl_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(self.stddev_pl_data_label, row, 2)

        # account value header
        row += 1
        label = QLabel()
        label.setText('Account Value')
        label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(label, row, 1)
        # account value data label
        self.account_value_data_label = QLabel()
        self.account_value_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(self.account_value_data_label, row, 2)

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
