from typing import List

from PyQt6.QtWidgets import QWidget, QHBoxLayout

from StockBench.controllers.controller_factory import StockBenchControllerFactory
from StockBench.controllers.stockbench_controller import StockBenchController
from StockBench.gui.palette.palette import Palette
from StockBench.gui.results.multi.multi_results_window import MultiResultsWindow


class CompareResultsWindow(QWidget):
    def __init__(self, stockbench_controller: StockBenchController, simulation_symbols: List[str], strategy1,
                 strategy2, simulation_logging, simulation_reporting, initial_balance, results_depth):
        super().__init__()
        self.setWindowTitle('Simulation Results')
        self.setStyleSheet(Palette.WINDOW_STYLESHEET)

        self.layout = QHBoxLayout()

        self.simulation_widget_1 = MultiResultsWindow(
            stockbench_controller,
            simulation_symbols,
            strategy1,
            initial_balance,
            simulation_logging,
            simulation_reporting,
            False,
            results_depth)

        # NOTE: Since compare requires 2 different simulator instances, we need to create another controller instance
        # using the factory, this time with an identifier of 2 so that the simulators do not use the same logger, and
        # we do not create the issue where log messages are duplicated.
        secondary_stockbench_controller = StockBenchControllerFactory.get_controller_instance(simulator_identifier=2)

        self.simulation_widget_2 = MultiResultsWindow(
            secondary_stockbench_controller,  # uses secondary controller instead
            simulation_symbols,
            strategy2,
            initial_balance,
            simulation_logging,
            simulation_reporting,
            True,  # prevent the second chart from loading the temp chart (being used by sim 1)
            results_depth)

        self.simulation_widget_1.begin()

        self.simulation_widget_2.begin()

        self.layout.addWidget(self.simulation_widget_1)
        self.layout.addWidget(self.simulation_widget_2)

        self.setLayout(self.layout)
