from PyQt6.QtWidgets import QLabel
from time import perf_counter
from StockBench.gui.results.base.results_window import SimulationResultsWindow
from StockBench.gui.results.folder.tabs.folder_overview_tab import FolderOverViewTab
from StockBench.gui.results.folder.tabs.folder_trades_made_tab import FolderTradesMadeTab
from StockBench.gui.results.folder.tabs.folder_effectiveness_tab import FolderEffectivenessTab
from StockBench.gui.results.folder.tabs.folder_average_pl_tab import FolderAverageProfitLossTab
from StockBench.gui.results.folder.tabs.folder_median_pl_tab import FolderMedianProfitLossTab

from StockBench.gui.results.folder.tabs.folder_positions_histogram_tab import FolderPositionsHistogramTab


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
        self.layout.addWidget(self.progress_bar)
        # tab creation
        self.overview_tab = FolderOverViewTab(strategies, self.progress_observers)
        self.trades_made_tab = FolderTradesMadeTab()
        self.effectiveness_tab = FolderEffectivenessTab()
        self.average_pl_tab = FolderAverageProfitLossTab()
        self.median_pl_tab = FolderMedianProfitLossTab()
        self.positions_histogram_tab = FolderPositionsHistogramTab()

        # tab widget
        self.tab_widget.addTab(self.overview_tab, 'Overview')
        self.tab_widget.addTab(self.trades_made_tab, 'Trades Made')
        self.tab_widget.addTab(self.effectiveness_tab, 'Effectiveness')
        self.tab_widget.addTab(self.average_pl_tab, 'Average P/L')
        self.tab_widget.addTab(self.median_pl_tab, 'Median P/L')
        self.tab_widget.addTab(self.positions_histogram_tab, 'Positions (histogram)')
        self.layout.addWidget(self.tab_widget)

        # error message
        self.error_message_label = QLabel()
        self.layout.addWidget(self.error_message_label)

        self.setLayout(self.layout)

    def update_error_message(self, message: str):
        self.error_message_label.setText(message)

    def _update_progress_bar(self):
        max_progress_per_observer = int(100 / len(self.progress_observers))
        progress = 0

        all_bars_complete = True
        for i, progress_observer in enumerate(self.progress_observers):
            if progress_observer.is_simulation_completed():
                # full progress for that observer
                progress += max_progress_per_observer
            else:
                # partial progress for that observer (scaled to the progress bar as a whole)
                progress += max_progress_per_observer * int(progress_observer.get_progress() / 100)
                all_bars_complete = False

        self.progress_bar.setValue(progress)

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
                                                       results_depth=self.simulator.DATA_ONLY,
                                                       save_option=save_option,
                                                       progress_observer=self.progress_observers[i]))

        elapsed_time = round(perf_counter() - start_time, 2)

        return {"results": results, 'elapsed_time': elapsed_time}

    def _render_data(self, simulation_results: dict):
        self.overview_tab.render_data(simulation_results)
        self.trades_made_tab.render_data(simulation_results)
        self.effectiveness_tab.render_data(simulation_results)
        self.average_pl_tab.render_data(simulation_results)
        self.median_pl_tab.render_data(simulation_results)
        self.positions_histogram_tab.render_data(simulation_results)

    @staticmethod
    def _get_strategy_name(filepath: str):
        filepath = filepath.replace('\\', '/')
        return filepath.split('/')[-1].split('.')[0]
