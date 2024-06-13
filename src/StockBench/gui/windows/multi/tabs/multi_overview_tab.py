import logging
from PyQt6.QtWidgets import QLabel
from StockBench.gui.windows.base.overview_tab import OverviewTab, OverviewSideBar, OverviewTable

log = logging.getLogger()


class MultiOverviewTab(OverviewTab):
    """Tab showing simulation overview for multi-symbol simulation results."""
    def __init__(self, progress_observer):
        super().__init__()
        # add components to the layout
        self.overview_side_bar = MultiOverviewSideBar(progress_observer)
        self.layout.addWidget(self.overview_side_bar)
        self.overview_side_bar.setMaximumWidth(300)
        self.layout.addWidget(self.html_viewer)

        # apply the layout
        self.setLayout(self.layout)

    def render_data(self, simulation_results):
        self.render_chart(simulation_results)
        self.overview_side_bar.render_data(simulation_results)

    def update_error_message(self, message):
        # pass the error down
        self.overview_side_bar.update_error_message(message)


class MultiOverviewSideBar(OverviewSideBar):
    """Sidebar that stands next to the overview chart."""
    def __init__(self, progress_observer):
        super().__init__(progress_observer)
        self.simulation_results_to_export = {}

        # add components to the layout
        self.layout.addWidget(self.results_header)

        self.overview_table = MultiOverviewTable()
        self.layout.addWidget(self.overview_table)

        self.layout.addWidget(self.export_json_btn)

        self.layout.addWidget(self.export_excel_btn)

        # pushes the status header and output box to the bottom
        self.layout.addStretch()

        self.layout.addWidget(self.status_header)
        self.layout.addWidget(self.output_box)

        # apply the layout
        self.setLayout(self.layout)

    def render_data(self, simulation_results):
        # save the results to allow exporting
        self.simulation_results_to_export = simulation_results
        # render data in child components
        self.overview_table.render_data(simulation_results)

    def _remove_extraneous_info(self, results: dict) -> dict:
        """Remove info from the simulation results that is not relevant to exporting."""
        export_dict = results.copy()

        # remove extraneous data from exported results
        export_dict.pop('elapsed_time')
        export_dict.pop('buy_rule_analysis_chart_filepath')
        export_dict.pop('sell_rule_analysis_chart_filepath')
        export_dict.pop('position_analysis_chart_filepath')
        export_dict.pop('overview_chart_filepath')

        return export_dict


class MultiOverviewTable(OverviewTable):
    """Widget that houses the numerical results table."""
    def __init__(self):
        super().__init__()
        # strategy header
        row = 1
        label = QLabel()
        label.setText('Strategy')
        label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(label, row, 1)
        # strategy data label
        self.strategy_data_label = QLabel()
        self.strategy_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(self.strategy_data_label, row, 2)

        # elapsed time header
        row += 1
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

        # apply the layout to the frame
        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        if simulation_results.keys():
            self.strategy_data_label.setText(f'{simulation_results["strategy"]}')
            self.elapsed_time_data_label.setText(f'{simulation_results["elapsed_time"]} seconds')
            self.trades_made_data_label.setText(f'{simulation_results["trades_made"]}')
            self.effectiveness_data_label.setText(f'{simulation_results["effectiveness"]} %')
            self.total_pl_data_label.setText(f'$ {simulation_results["total_profit_loss"]}')
            self.average_pl_data_label.setText(f'$ {simulation_results["average_profit_loss"]}')
            self.median_pl_data_label.setText(f'$ {simulation_results["median_profit_loss"]}')
            self.stddev_pl_data_label.setText(f'$ {simulation_results["standard_profit_loss_deviation"]}')
