import traceback
from typing import Callable, List

import requests

from StockBench.controllers.charting.exceptions import ChartingError
from StockBench.controllers.charting.multi.multi_charting_engine import MultiChartingEngine
from StockBench.controllers.charting.singular.singular_charting_engine import SingularChartingEngine
from StockBench.controllers.proxies.charting_proxy import ChartingProxy
from StockBench.controllers.proxies.simulation_proxy import SimulationProxy
from StockBench.controllers.simulator.algorithm.exceptions import MalformedStrategyError
from StockBench.controllers.simulator.broker.broker_client import MissingCredentialError, InvalidSymbolError, \
    InsufficientDataError
from StockBench.controllers.simulator.indicator.exceptions import StrategyIndicatorError
from StockBench.controllers.simulator.simulator import Simulator
from StockBench.models.constants.simulation_results_constants import *
from StockBench.models.observers.progress_observer import ProgressObserver
from StockBench.models.simulation_result.simulation_result import SimulationResult
from StockBench.models.constants.chart_filepath_key_constants import *


class StockBenchController:
    """Controller for interacting with the StockBench Simulation suite."""
    MESSAGE = 'message'

    def __init__(self, simulator: Simulator, singular_charting_engine: SingularChartingEngine,
                 multi_charting_engine: MultiChartingEngine):
        self.__simulator = simulator
        self.__singular_charting_engine = singular_charting_engine
        self.__multi_charting_engine = multi_charting_engine

    def singular_simulation(self, strategy: dict, symbol: str, initial_balance: float, logging_on: bool,
                            reporting_on: bool, unique_chart_saving: bool, results_depth: int, show_volume: bool,
                            progress_observer: ProgressObserver) -> SimulationResult:
        """Controller for running singular-symbol simulations and building charts."""
        simulation_results = SimulationProxy.run_singular_simulation(self.__simulator, strategy, symbol,
                                                                     initial_balance, logging_on, reporting_on,
                                                                     progress_observer)

        if 'status_code' in simulation_results.keys():
            # simulation failed
            return SimulationResult(
                status_code=400,
                message=simulation_results[self.MESSAGE],
                simulation_results={},
                chart_filepaths=ChartingProxy.SINGULAR_DEFAULT_CHART_FILEPATHS)

        chart_filepaths = ChartingProxy.build_singular_charts(self.__singular_charting_engine, simulation_results,
                                                              unique_chart_saving, results_depth, show_volume)

        if 'status_code' in chart_filepaths.keys():
            # charting failed
            return SimulationResult(
                status_code=400,
                message=simulation_results[self.MESSAGE],
                simulation_results={},
                chart_filepaths=ChartingProxy.SINGULAR_DEFAULT_CHART_FILEPATHS)

        # success
        return SimulationResult(
            status_code=200,
            message='',
            simulation_results=simulation_results,
            chart_filepaths=chart_filepaths)

    def multi_simulation(self, strategy: dict, symbols: List[str], initial_balance: float, logging_on: bool,
                         reporting_on: bool, unique_chart_saving: bool, results_depth: int,
                         progress_observer: ProgressObserver):
        """Controller for running multi-symbol simulations and building charts."""
        simulation_results = SimulationProxy.run_multi_simulation(self.__simulator, strategy, symbols, initial_balance,
                                                                  logging_on, reporting_on, progress_observer)

        if 'status_code' in simulation_results.keys():
            # simulation failed
            return SimulationResult(
                status_code=400,
                message=simulation_results[self.MESSAGE],
                simulation_results={},
                chart_filepaths=ChartingProxy.MULTI_DEFAULT_CHART_FILEPATHS)

        chart_filepaths = ChartingProxy.build_multi_charts(self.__multi_charting_engine, simulation_results,
                                                           unique_chart_saving, results_depth)

        if 'status_code' in chart_filepaths.keys():
            # charting failed
            return SimulationResult(
                status_code=400,
                message=simulation_results[self.MESSAGE],
                simulation_results={},
                chart_filepaths=ChartingProxy.MULTI_DEFAULT_CHART_FILEPATHS)

        # success
        return SimulationResult(
            status_code=200,
            message='',
            simulation_results=simulation_results,
            chart_filepaths=chart_filepaths)

    def folder_simulation(self):
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
