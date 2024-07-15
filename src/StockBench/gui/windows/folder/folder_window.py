from PyQt6.QtWidgets import QProgressBar, QLabel, QTableWidget, QTableWidgetItem
from PyQt6.QtGui import QBrush, QColor
from time import perf_counter
from StockBench.gui.palette.palette import Palette
from StockBench.gui.windows.base.results_window import SimulationResultsWindow
from StockBench.gui.windows.folder.tabs.folder_overview_tab import FolderResultsTab


class FolderResultsWindow(SimulationResultsWindow):
    def __init__(self, strategies, symbols, initial_balance, simulator, progress_observer, worker, logging_on,
                 reporting_on, unique_chart_saving_on, results_depth):
        # pass 1st strategy as a dummy strategy because we will load the strategy dynamically in _run_simulation
        super().__init__(strategies[0], initial_balance, simulator, progress_observer, worker, logging_on,
                         reporting_on, unique_chart_saving_on, results_depth)
        self.strategies = strategies
        self.symbols = symbols
        self.simulator = simulator(initial_balance)  # instantiate the class reference
        self.progress_observer = progress_observer  # store the class reference
        self.worker = worker
        self.logging = logging_on
        self.reporting = reporting_on
        self.unique_chart_saving = unique_chart_saving_on
        self.results_depth = results_depth
        self.worker = worker

        # create a list of progress observers for each strategy
        self.progress_observers = [progress_observer() for _ in strategies]

        # add elements to the layout

        # create a list of progress bars for each strategy
        self.progress_bars = [QProgressBar() for _ in strategies]
        # set up the progress bars and add them to the layout
        self.__setup_progress_bars()

        self.results_frame = FolderResultsTab(strategies, self.progress_observers)
        self.layout.addWidget(self.results_frame)

        # error message
        self.error_message_label = QLabel()
        self.layout.addWidget(self.error_message_label)

        self.setLayout(self.layout)

    def update_error_message(self, message: str):
        # pass the error down
        self.error_message_label.setText(message)

    def __setup_progress_bars(self):
        for progress_bar in self.progress_bars:
            progress_bar.setRange(0, 100)
            progress_bar.setFixedHeight(5)
            progress_bar.setTextVisible(False)
            progress_bar.setStyleSheet(Palette.PROGRESS_BAR_STYLESHEET)
            self.layout.addWidget(progress_bar)

    def _update_progress_bar(self):
        all_bars_complete = True
        for i, progress_observer in enumerate(self.progress_observers):
            if progress_observer.is_simulation_completed():
                # mark the progress bar as completed
                self.progress_bars[i].setValue(100)
            else:
                # update the progress bar
                self.progress_bars[i].setValue(int(progress_observer.get_progress()))
                all_bars_complete = False

        if all_bars_complete:
            # stop the timer
            self.timer.stop()

    def _run_simulation(self, save_option) -> dict:
        results = []

        start_time = perf_counter()
        # run all simulations (using matched progress observer)
        for i, strategy in enumerate(self.strategies):
            # __run_simulation sets the simulator to use self.strategy
            # we passed in a dummy strategy to satisfy the constructor (self.strategy gets set to dummy)
            # override the dummy strategy in the simulator with the correct one
            self.simulator.load_strategy(strategy)

            results.append(self.simulator.run_multiple(self.symbols,
                                                       results_depth=self.results_depth,
                                                       save_option=save_option,
                                                       progress_observer=self.progress_observers[i]))

        elapsed_time = round(perf_counter() - start_time, 2)

        return {"results": results, 'elapsed_time': elapsed_time}

    def _render_data(self, simulation_results: dict):
        self.results_frame.render_data(simulation_results)
