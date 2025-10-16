import traceback
from typing import Callable

import requests

from StockBench.controllers.charting.charting_engine import ChartingEngine
from StockBench.controllers.charting.exceptions import ChartingError
from StockBench.controllers.charting.singular.singular_charting_engine import SingularChartingEngine
from StockBench.controllers.simulator.algorithm.exceptions import MalformedStrategyError
from StockBench.controllers.simulator.broker.broker_client import MissingCredentialError, InvalidSymbolError, \
    InsufficientDataError
from StockBench.controllers.simulator.indicator.exceptions import StrategyIndicatorError
from StockBench.controllers.simulator.simulator import Simulator
from StockBench.models.constants.general_constants import BUY_SIDE, SELL_SIDE
from StockBench.models.constants.simulation_results_constants import *
from StockBench.models.observers.progress_observer import ProgressObserver
from StockBench.models.simulation_result.simulation_result import SimulationResult
from StockBench.models.constants.chart_filepath_key_constants import *


class StockBenchController:
    @staticmethod
    def singular_simulation(strategy: dict, symbol: str, initial_balance: float, logging_on: bool, reporting_on: bool,
                            unique_chart_saving: int, results_depth: int, show_volume: bool,
                            progress_observer: ProgressObserver) -> SimulationResult:
        simulator = Simulator(initial_balance)

        simulator.load_strategy(strategy)

        if logging_on:
            simulator.enable_logging()
        if reporting_on:
            simulator.enable_reporting()

        if unique_chart_saving:
            chart_saving = ChartingEngine.UNIQUE_SAVE
        else:
            chart_saving = ChartingEngine.TEMP_SAVE

        simulation_results = StockBenchController.__run_simulation_with_error_catching(
            simulator.run, symbol, progress_observer)

        # FIXME: move constants to 1 file
        if results_depth == Simulator.CHARTS_AND_DATA:
            chart_filepaths = {
                OVERVIEW_CHART_FILEPATH_KEY: SingularChartingEngine.build_singular_overview_chart(
                    simulation_results[NORMALIZED_SIMULATION_DATA], simulation_results[SYMBOL_KEY],
                    simulation_results[AVAILABLE_INDICATORS], show_volume, chart_saving),
                ACCOUNT_VALUE_LINE_CHART_FILEPATH_KEY: SingularChartingEngine.build_account_value_line_chart(
                    simulation_results[NORMALIZED_SIMULATION_DATA][Simulator.ACCOUNT_VALUE_COLUMN_NAME].tolist(),
                    simulation_results[SYMBOL_KEY], chart_saving),
                BUY_RULES_BAR_CHART_FILEPATH_KEY: ChartingEngine.build_rules_bar_chart(
                    simulation_results[POSITIONS_KEY], BUY_SIDE, simulation_results[SYMBOL_KEY], chart_saving),
                SELL_RULES_BAR_CHART_FILEPATH_KEY: ChartingEngine.build_rules_bar_chart(
                    simulation_results[POSITIONS_KEY], SELL_SIDE, simulation_results[SYMBOL_KEY], chart_saving),
                POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY: ChartingEngine.build_positions_duration_bar_chart(
                    simulation_results[POSITIONS_KEY], simulation_results[SYMBOL_KEY], chart_saving),
                POSITIONS_PL_BAR_CHART_FILEPATH_KEY: ChartingEngine.build_positions_profit_loss_bar_chart(
                    simulation_results[POSITIONS_KEY], simulation_results[SYMBOL_KEY], chart_saving),
                POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH_KEY:
                    SingularChartingEngine.build_single_strategy_result_dataset_positions_plpc_histogram_chart(
                        simulation_results[POSITIONS_KEY], simulation_results[SYMBOL_KEY],
                        simulation_results[STRATEGY_KEY], chart_saving),
                POSITIONS_PLPC_BOX_PLOT_CHART_FILEPATH_KEY:
                    SingularChartingEngine.build_single_strategy_result_dataset_positions_plpc_box_plot(
                        simulation_results[POSITIONS_KEY], simulation_results[STRATEGY_KEY],
                        simulation_results[SYMBOL_KEY], chart_saving)
            }
        else:
            # filepaths are set to empty strings which will cause the html viewers to render chart unavailable
            chart_filepaths = {
                OVERVIEW_CHART_FILEPATH_KEY: '',
                ACCOUNT_VALUE_LINE_CHART_FILEPATH_KEY: '',
                BUY_RULES_BAR_CHART_FILEPATH_KEY: '',
                SELL_RULES_BAR_CHART_FILEPATH_KEY: '',
                POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY: '',
                POSITIONS_PL_BAR_CHART_FILEPATH_KEY: '',
                POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH_KEY: '',
                POSITIONS_PLPC_BOX_PLOT_CHART_FILEPATH_KEY: ''
            }

        return SimulationResult(
            status_code=simulation_results[0],
            message=simulation_results[1],
            simulation_results=simulation_results[2],
            chart_filepaths=chart_filepaths)

    @staticmethod
    def multi_simulation():
        pass

    @staticmethod
    def folder_simulation():
        pass

    @staticmethod
    def __run_simulation_with_error_catching(simulation_function: Callable, *args) -> tuple:
        # run the simulation and catch any errors - keep the app from crashing even if the sim fails
        status_code = 200
        message = ''
        results = {}
        try:
            results = simulation_function(args)
        except requests.exceptions.ConnectionError:
            message = 'Failed to connect to broker!'
        except MalformedStrategyError as e:
            message = f'Malformed strategy error: {e}'
        except StrategyIndicatorError as e:
            message = f'Strategy error: {e}'
        except ChartingError as e:
            message = f'Charting error: {e}'
        except MissingCredentialError as e:
            message = f'Missing credential error: {e}'
        except InvalidSymbolError as e:
            message = f'Invalid symbol error: {e}'
        except InsufficientDataError as e:
            message = f'Insufficient data error {e}'
        except Exception as e:
            message = f'Unexpected error: {type(e)} {e} {traceback.print_exc()}'

        if message:
            status_code = 400

        return status_code, message, results
