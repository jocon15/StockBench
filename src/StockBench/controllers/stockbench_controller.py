from time import perf_counter
from typing import List

from StockBench.controllers.charting.folder.folder_charting_engine import FolderChartingEngine
from StockBench.controllers.charting.multi.multi_charting_engine import MultiChartingEngine
from StockBench.controllers.charting.singular.singular_charting_engine import SingularChartingEngine
from StockBench.controllers.proxies.charting_proxy import ChartingProxy
from StockBench.controllers.proxies.simulation_proxy import SimulationProxy
from StockBench.controllers.simulator.simulator import Simulator
from StockBench.models.constants.simulation_results_constants import *
from StockBench.models.observers.progress_observer import ProgressObserver
from StockBench.models.simulation_result.simulation_result import SimulationResult


class StockBenchController:
    """Controller for interacting with the StockBench Simulation suite."""
    RESULTS = 'results'
    MESSAGE = 'message'

    def __init__(self, simulator: Simulator, singular_charting_engine: SingularChartingEngine,
                 multi_charting_engine: MultiChartingEngine, folder_charting_engine: FolderChartingEngine):
        self.__simulator = simulator
        self.__singular_charting_engine = singular_charting_engine
        self.__multi_charting_engine = multi_charting_engine
        self.__folder_charting_engine = folder_charting_engine

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
                message=chart_filepaths[self.MESSAGE],
                simulation_results={},
                chart_filepaths=ChartingProxy.SINGULAR_DEFAULT_CHART_FILEPATHS)

        return SimulationResult(
            status_code=200,
            message='',
            simulation_results=simulation_results,
            chart_filepaths=chart_filepaths)

    def multi_simulation(self, strategy: dict, symbols: List[str], initial_balance: float, logging_on: bool,
                         reporting_on: bool, unique_chart_saving: bool, results_depth: int,
                         progress_observer: ProgressObserver) -> SimulationResult:
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
                message=chart_filepaths[self.MESSAGE],
                simulation_results={},
                chart_filepaths=ChartingProxy.MULTI_DEFAULT_CHART_FILEPATHS)

        return SimulationResult(
            status_code=200,
            message='',
            simulation_results=simulation_results,
            chart_filepaths=chart_filepaths)

    def folder_simulation(self, strategies: List[dict], symbols: List[str], initial_balance: float, logging_on: bool,
                          reporting_on: bool, progress_observers: List[ProgressObserver]) -> SimulationResult:
        """Controller for running folder simulations and building charts."""
        start_time = perf_counter()
        simulation_results = SimulationProxy.run_folder_simulation(self.__simulator, strategies, symbols,
                                                                   initial_balance, logging_on, reporting_on,
                                                                   progress_observers)

        if 'status_code' in simulation_results.keys():
            # simulation failed
            return SimulationResult(
                status_code=400,
                message=simulation_results[self.MESSAGE],
                simulation_results={},
                chart_filepaths=ChartingProxy.FOLDER_DEFAULT_CHART_FILEPATHS)

        chart_filepaths = ChartingProxy.build_folder_charts(self.__folder_charting_engine,
                                                            simulation_results[self.RESULTS])

        simulation_results[ELAPSED_TIME_KEY] = round(perf_counter() - start_time, 2)

        if 'status_code' in chart_filepaths.keys():
            # charting failed
            return SimulationResult(
                status_code=400,
                message=chart_filepaths[self.MESSAGE],
                simulation_results={},
                chart_filepaths=ChartingProxy.FOLDER_DEFAULT_CHART_FILEPATHS)

        return SimulationResult(
            status_code=200,
            message='',
            simulation_results=simulation_results,
            chart_filepaths=chart_filepaths)
