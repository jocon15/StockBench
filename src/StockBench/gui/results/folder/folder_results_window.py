from time import perf_counter
from PyQt6.QtWidgets import QLabel

from StockBench.controllers.charting.folder import FolderChartingEngine
from StockBench.gui.models.simulation_results_bundle import SimulationResultsBundle
from StockBench.gui.results.base.results_window import SimulationResultsWindow

from StockBench.gui.results.folder.tabs.folder_overview_tab import FolderOverViewTab
from StockBench.gui.results.folder.tabs.folder_positions_box_plot_tab import FolderPositionsBoxPlotTabVertical
from StockBench.gui.results.folder.tabs.folder_trades_made_tab import FolderTradesMadeTabVertical
from StockBench.gui.results.folder.tabs.folder_effectiveness_tab import FolderEffectivenessTabVertical
from StockBench.gui.results.folder.tabs.folder_total_pl_tab import FolderTotalProfitLossTabVertical
from StockBench.gui.results.folder.tabs.folder_average_pl_tab import FolderAverageProfitLossTabVertical
from StockBench.gui.results.folder.tabs.folder_median_pl_tab import FolderMedianProfitLossTabVertical
from StockBench.gui.results.folder.tabs.folder_stddev_pl_tab import FolderStandardDeviationProfitLossTabVertical
from StockBench.gui.results.folder.tabs.folder_positions_histogram_tab import FolderPositionsHistogramTabVertical
from StockBench.models.observers.progress_observer import ProgressObserver
from StockBench.constants import *
from StockBench.gui.results.folder.constants.constants import *


class FolderResultsWindow(SimulationResultsWindow):
    def __init__(self, strategies, symbols, initial_balance, logging_on, reporting_on, unique_chart_saving_on,
                 results_depth):
        # pass 1st strategy as a dummy strategy because we will load the strategy dynamically in _run_simulation
        super().__init__(strategies[0], initial_balance, logging_on, reporting_on, unique_chart_saving_on,
                         results_depth)
        self.strategies = strategies
        self.symbols = symbols
        self.logging = logging_on
        self.reporting = reporting_on
        self.unique_chart_saving = unique_chart_saving_on
        self.results_depth = results_depth

        # create a list of progress observers for each strategy
        self.progress_observers = [ProgressObserver() for _ in strategies]

        # add elements to the layout
        self.layout.addWidget(self.progress_bar)
        # tab creation
        self.overview_tab = FolderOverViewTab(strategies, self.progress_observers)
        self.trades_made_tab = FolderTradesMadeTabVertical()
        self.effectiveness_tab = FolderEffectivenessTabVertical()
        self.total_pl_tab = FolderTotalProfitLossTabVertical()
        self.average_pl_tab = FolderAverageProfitLossTabVertical()
        self.median_pl_tab = FolderMedianProfitLossTabVertical()
        self.stddev_pl_tab = FolderStandardDeviationProfitLossTabVertical()
        self.positions_plpc_histogram_tab = FolderPositionsHistogramTabVertical()
        self.positions_plpc_box_plot_tab = FolderPositionsBoxPlotTabVertical()

        # tab widget
        self.tab_widget.addTab(self.overview_tab, 'Overview')
        self.tab_widget.addTab(self.trades_made_tab, 'Trades Made')
        self.tab_widget.addTab(self.effectiveness_tab, 'Effectiveness')
        self.tab_widget.addTab(self.total_pl_tab, 'Total P/L')
        self.tab_widget.addTab(self.average_pl_tab, 'Average P/L')
        self.tab_widget.addTab(self.median_pl_tab, 'Median P/L')
        self.tab_widget.addTab(self.stddev_pl_tab, 'Stddev P/L')
        self.tab_widget.addTab(self.positions_plpc_histogram_tab, 'Positions P/L % (histogram)')
        self.tab_widget.addTab(self.positions_plpc_box_plot_tab, 'Positions P/L % (box plot)')
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
        for progress_observer in self.progress_observers:
            if progress_observer.is_simulation_completed():
                # full progress for that observer
                progress += max_progress_per_observer
            else:
                # partial progress for that observer (scaled to the progress bar as a whole)
                progress += max_progress_per_observer * (progress_observer.get_progress() / 100)
                all_bars_complete = False

        self.progress_bar.setValue(progress)

        if all_bars_complete:
            # set bar to full
            self.progress_bar.setValue(100)
            self.timer.stop()

    def _run_simulation(self, save_option: int, results_depth: int) -> SimulationResultsBundle:
        results = []

        start_time = perf_counter()
        # run all simulations (using matched progress observer)
        for i, strategy in enumerate(self.strategies):
            # __run_simulation sets the simulator to use self.strategy
            # we passed in a dummy strategy to satisfy the constructor (self.strategy gets set to dummy)
            # override the dummy strategy in the simulator with the correct one
            self.simulator.load_strategy(strategy)

            results.append(self.simulator.run_multiple(self.symbols, self.progress_observers[i]))

        # results depth is not an option for folder, no need for dummy dict
        chart_filepaths = {
            TRADES_MADE_BAR_CHART_FILEPATH_KEY: FolderChartingEngine.build_trades_made_bar_chart(results),
            EFFECTIVENESS_BAR_CHART_FILEPATH_KEY: FolderChartingEngine.build_effectiveness_bar_chart(results),
            TOTAL_PL_BAR_CHART_FILEPATH_KEY: FolderChartingEngine.build_total_pl_bar_chart(results),
            AVERAGE_PL_BAR_CHART_FILEPATH_KEY: FolderChartingEngine.build_average_pl_bar_chart(results),
            MEDIAN_PL_BAR_CHART_FILEPATH_KEY: FolderChartingEngine.build_median_pl_bar_chart(results),
            STDDEV_PL_BAR_CHART_FILEPATH_KEY: FolderChartingEngine.build_stddev_pl_bar_chart(results),
            POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH_KEY:
                FolderChartingEngine.build_positions_plpc_histogram_chart(results),
            POSITIONS_PLPC_BOX_PLOT_CHART_FILEPATH_KEY: FolderChartingEngine.build_positions_plpc_box_chart(results)
        }

        elapsed_time = round(perf_counter() - start_time, 2)

        return SimulationResultsBundle(simulation_results={'results': results, ELAPSED_TIME_KEY: elapsed_time},
                                       chart_filepaths=chart_filepaths)

    def _render_data(self, simulation_results_bundle: SimulationResultsBundle):
        # only run if all symbols had enough data
        if 'results' in simulation_results_bundle.simulation_results.keys():
            self.overview_tab.render_data(simulation_results_bundle)
            self.trades_made_tab.render_chart(simulation_results_bundle.chart_filepaths)
            self.effectiveness_tab.render_chart(simulation_results_bundle.chart_filepaths)
            self.total_pl_tab.render_chart(simulation_results_bundle.chart_filepaths)
            self.average_pl_tab.render_chart(simulation_results_bundle.chart_filepaths)
            self.median_pl_tab.render_chart(simulation_results_bundle.chart_filepaths)
            self.stddev_pl_tab.render_chart(simulation_results_bundle.chart_filepaths)
            self.positions_plpc_histogram_tab.render_chart(simulation_results_bundle.chart_filepaths)
            self.positions_plpc_box_plot_tab.render_chart(simulation_results_bundle.chart_filepaths)
        else:
            # the simulation failed - render the chart unavailable html
            self.overview_tab.html_viewer.render_chart_unavailable()
            self.trades_made_tab.html_viewer.render_chart_unavailable()
            self.effectiveness_tab.html_viewer.render_chart_unavailable()
            self.total_pl_tab.html_viewer.render_chart_unavailable()
            self.average_pl_tab.html_viewer.render_chart_unavailable()
            self.median_pl_tab.html_viewer.render_chart_unavailable()
            self.stddev_pl_tab.html_viewer.render_chart_unavailable()
            self.positions_plpc_histogram_tab.html_viewer.render_chart_unavailable()
            self.positions_plpc_box_plot_tab.html_viewer.render_chart_unavailable()

    @staticmethod
    def _get_strategy_name(filepath: str):
        filepath = filepath.replace('\\', '/')
        return filepath.split('/')[-1].split('.')[0]
