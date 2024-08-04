from PyQt6.QtWidgets import QLabel
from StockBench.gui.results.base.overview_tab import OverviewTab, OverviewSideBar, OverviewTable


class SingularOverviewTab(OverviewTab):
    """Tab showing simulation overview for single-symbol simulation results."""
    def __init__(self, progress_observer):
        super().__init__()
        # add shared_components to the layout
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
        # add shared_components to the layout
        self.layout.addWidget(self.metadata_header)

        self.metadata_table = SingularMetadataOverviewTable()
        self.layout.addWidget(self.metadata_table)

        self.layout.addWidget(self.results_header)

        self.results_table = SingularResultsOverviewTable()
        self.layout.addWidget(self.results_table)

        self.layout.addWidget(self.export_json_btn)

        self.layout.addWidget(self.export_excel_btn)

        # pushes the status header and output box to the bottom
        self.layout.addStretch()

        self.layout.addWidget(self.status_header)
        self.layout.addWidget(self.output_box)

        # apply the layout
        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        # save the results to allow exporting
        self.simulation_results_to_export = simulation_results
        # render data in child shared_components
        self.metadata_table.render_data(simulation_results)
        self.results_table.render_data(simulation_results)

    def _remove_extraneous_info(self, results: dict) -> dict:
        """Remove info from the simulation results that is not relevant to exporting."""
        export_dict = results.copy()

        # remove extraneous data from exported results
        export_dict.pop('symbol')
        export_dict.pop('trade_able_days')
        export_dict.pop('elapsed_time')
        export_dict.pop('buy_rule_analysis_chart_filepath')
        export_dict.pop('sell_rule_analysis_chart_filepath')
        export_dict.pop('position_analysis_chart_filepath')
        export_dict.pop('overview_chart_filepath')

        return export_dict


class SingularMetadataOverviewTable(OverviewTable):
    """Table of overview metadata."""
    def __init__(self):
        super().__init__()
        # strategy label and data label
        row = 1
        self.layout.addWidget(self.strategy_label, row, 1)
        self.layout.addWidget(self.strategy_data_label, row, 2)

        # symbol header (not shared with multi)
        row += 1
        label = QLabel()
        label.setText('Symbol')
        label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(label, row, 1)
        # symbol data label (not shared with multi)
        self.symbol_data_label = QLabel()
        self.symbol_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        self.layout.addWidget(self.symbol_data_label, row, 2)

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
            self.symbol_data_label.setText(f'{simulation_results["symbol"]}')
            self.trade_able_days_data_label.setText(f'{simulation_results["trade_able_days"]} days')
            self.elapsed_time_data_label.setText(f'{simulation_results["elapsed_time"]} seconds')


class SingularResultsOverviewTable(OverviewTable):
    """Table of overview results data."""
    def __init__(self):
        super().__init__()
        # trades made label and data label
        row = 1
        self.layout.addWidget(self.trades_made_label, row, 1)
        self.layout.addWidget(self.trades_made_data_label, row, 2)

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
