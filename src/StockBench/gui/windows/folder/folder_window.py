from PyQt6.QtWidgets import QProgressBar, QLabel, QTableWidget, QTableWidgetItem
from StockBench.gui.palette.palette import Palette
from StockBench.gui.windows.base.results_window import SimulationResultsWindow


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
        self.results_frame = self  # instead of having a child results frame, this window is the results frame

        # create a list of progress observers for each strategy
        self.progress_observers = [progress_observer() for _ in strategies]

        # add elements to the layout

        # create a list of progress bars for each strategy
        self.progress_bars = [QProgressBar() for _ in strategies]
        # set up the progress bars and add them to the layout
        self.__setup_progress_bars()

        # table
        self.table = QTableWidget()
        self.table.setRowCount(len(strategies))
        self.table.setColumnCount(7)
        self.layout.addWidget(self.table)

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

        return {"results": results}

    def _render_data(self, simulation_results: dict):
        results = simulation_results['results']

        for row, result in enumerate(results):
            self.table.setItem(row, 0, QTableWidgetItem(str(result['strategy'])))
            self.table.setItem(row, 1, QTableWidgetItem(str(result['trades_made'])))
            self.table.setItem(row, 2, QTableWidgetItem(str(result['effectiveness'])))
            self.table.setItem(row, 3, QTableWidgetItem(str(result['total_profit_loss'])))
            self.table.setItem(row, 4, QTableWidgetItem(str(result['average_profit_loss'])))
            self.table.setItem(row, 5, QTableWidgetItem(str(result['median_profit_loss'])))
            self.table.setItem(row, 6, QTableWidgetItem(str(result['standard_profit_loss_deviation'])))
