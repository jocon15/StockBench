import logging
from time import perf_counter
from typing import List

from StockBench.controllers.logging import LoggingController
from StockBench.controllers.proxies.charting_proxy import ChartingProxy
from StockBench.controllers.proxies.simulator_proxy import SimulatorProxy
from StockBench.models.constants.simulation_results_constants import *
from StockBench.models.observers.progress_observer import ProgressObserver
from StockBench.models.simulation_result.simulation_result import SimulationResult


class StockBenchController:
    """Controller for interacting with the StockBench Simulation suite."""
    STATUS_CODE = 'status_code'
    RESULTS = 'results'
    MESSAGE = 'message'

    def __init__(self, simulator_proxy: SimulatorProxy, charting_proxy: ChartingProxy):
        self.__simulator_proxy = simulator_proxy
        self.__charting_proxy = charting_proxy

    def singular_simulation(self, strategy: dict, symbol: str, initial_balance: float, logging_on: bool,
                            reporting_on: bool, unique_chart_saving: bool, results_depth: int, show_volume: bool,
                            progress_observer: ProgressObserver) -> SimulationResult:
        """Controller for running singular-symbol simulations and building charts."""
        if logging_on:
            LoggingController.enable_log_saving()

        simulation_results = self.__simulator_proxy.run_singular_simulation(strategy, symbol, initial_balance,
                                                                            reporting_on, progress_observer)

        if self.STATUS_CODE in simulation_results.keys():
            # simulation failed
            return SimulationResult(
                status_code=400,
                message=simulation_results[self.MESSAGE],
                simulation_results={},
                chart_filepaths=ChartingProxy.SINGULAR_DEFAULT_CHART_FILEPATHS)

        chart_filepaths = self.__charting_proxy.build_singular_charts(simulation_results, unique_chart_saving,
                                                                      results_depth, show_volume)

        if progress_observer:
            progress_observer.set_charting_complete()

        if self.STATUS_CODE in chart_filepaths.keys():
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
        if logging_on:
            LoggingController.enable_log_saving()

        simulation_results = self.__simulator_proxy.run_multi_simulation(strategy, symbols, initial_balance,
                                                                         reporting_on, progress_observer)

        if self.STATUS_CODE in simulation_results.keys():
            # simulation failed
            return SimulationResult(
                status_code=400,
                message=simulation_results[self.MESSAGE],
                simulation_results={},
                chart_filepaths=ChartingProxy.MULTI_DEFAULT_CHART_FILEPATHS)

        chart_filepaths = self.__charting_proxy.build_multi_charts(simulation_results, unique_chart_saving,
                                                                   results_depth)

        if progress_observer:
            progress_observer.set_charting_complete()

        if self.STATUS_CODE in chart_filepaths.keys():
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
        if logging_on:
            LoggingController.enable_log_saving()

        start_time = perf_counter()
        simulation_results = self.__simulator_proxy.run_folder_simulation(strategies, symbols, initial_balance,
                                                                          reporting_on, progress_observers)

        if self.STATUS_CODE in simulation_results.keys():
            # simulation failed
            return SimulationResult(
                status_code=400,
                message=simulation_results[self.MESSAGE],
                simulation_results={},
                chart_filepaths=ChartingProxy.FOLDER_DEFAULT_CHART_FILEPATHS)

        record = logging.LogRecord('', logging.INFO, __file__, 0, 'Building charts...', (), None, '', None)
        progress_observers[-1].add_log_record(record)

        chart_filepaths = self.__charting_proxy.build_folder_charts(simulation_results[self.RESULTS])

        record = logging.LogRecord('', logging.INFO, __file__, 0, 'Charting complete \u2705', (), None, '', None)
        progress_observers[-1].add_log_record(record)

        # mark all progress observers except the first one complete - using the first to record charting logs
        for progress_observer in progress_observers:
            progress_observer.set_charting_complete()

        simulation_results[ELAPSED_TIME_KEY] = round(perf_counter() - start_time, 2)

        if self.STATUS_CODE in chart_filepaths.keys():
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
