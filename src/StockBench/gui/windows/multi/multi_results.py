import os
import sys
import logging

log = logging.getLogger()

from PyQt6.QtWidgets import QVBoxLayout, QGridLayout, QHBoxLayout, QLabel

# current directory (peripherals)
current = os.path.dirname(os.path.realpath(__file__))

# parent filepath (src)
parent = os.path.dirname(current)

# add the parent (src) to path
sys.path.append(parent)

from StockBench.display.display import Display
from StockBench.gui.windows.results import SimulationResultsWindow, ResultsFrame, ResultsTable
from StockBench.gui.windows.multi.multi_rules_tab import MultiRulesTab


class MultiResultsWindow(SimulationResultsWindow):
    """Window that holds the progress bar and the results box."""
    def __init__(self, worker, simulator, progress_observer, initial_balance):
        super().__init__(worker, simulator, progress_observer, initial_balance)
        # get set by caller (MainWindow) after construction but before .show()
        self.symbols = None

        # define layout type
        self.layout = QVBoxLayout()

        # progress bar
        self.layout.addWidget(self.progress_bar)

        # simulation results frame (gets added to layout via tab widget
        self.results_frame = MultiResultsFrame()

        self.buy_rules_tab = MultiRulesTab('buy')
        self.sell_rules_tab = MultiRulesTab('sell')

        # tab widget
        self.tab_widget.addTab(self.results_frame, "Overview")
        self.tab_widget.addTab(self.buy_rules_tab, "Buy Rules (beta)")
        self.tab_widget.addTab(self.sell_rules_tab, "Sell Rules (beta)")
        self.layout.addWidget(self.tab_widget)

        # apply the layout to the window
        self.setLayout(self.layout)

    def run_simulation(self) -> dict:
        # load the strategy into the simulator
        if self.logging:
            self.simulator.enable_logging()
        if self.reporting:
            self.simulator.enable_reporting()
        self.simulator.load_strategy(self.strategy)
        if self.unique_chart_saving:
            save_option = Display.UNIQUE_SAVE
        else:
            save_option = Display.TEMP_SAVE
        try:
            return self.simulator.run_multiple(self.symbols, show_chart=False, save_option=save_option,
                                               progress_observer=self.progress_observer)
        except ValueError as e:
            # pass the error to the simulation results box
            self.results_frame.update_error_message(f'{e}')
            return {}

    def render_updated_data(self, simulation_results: dict):
        self.results_frame.render_data(simulation_results)
        self.buy_rules_tab.render_data(simulation_results)
        self.sell_rules_tab.render_data(simulation_results)


class MultiResultsFrame(ResultsFrame):
    """Widget that houses the simulation results box."""

    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()

        self.simulation_results_text_box = SimulationResultsTable()
        self.layout.addWidget(self.simulation_results_text_box)
        self.simulation_results_text_box.setMaximumWidth(300)
        self.simulation_results_text_box.setMaximumHeight(800)

        self.layout.addWidget(self.webView)

        self.setLayout(self.layout)

    def render_data(self, simulation_results):
        # render the chart
        self.render_chart(simulation_results)
        # render the text box results
        self.simulation_results_text_box.render_data(simulation_results)

    def update_error_message(self, message):
        # pass the error down to the simulation results text box
        self.simulation_results_text_box.update_error_message(message)


class SimulationResultsTable(ResultsTable):
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
