import traceback
from functools import wraps
from typing import Callable

from StockBench.controllers.charting.exceptions import ChartingError
from StockBench.controllers.charting.folder.folder_charting_engine import FolderChartingEngine
from StockBench.controllers.charting.multi.multi_charting_engine import MultiChartingEngine
from StockBench.controllers.charting.singular.singular_charting_engine import SingularChartingEngine
from StockBench.controllers.simulator.simulator import Simulator
from StockBench.models.constants.chart_filepath_key_constants import *
from StockBench.models.constants.general_constants import BUY_SIDE, SELL_SIDE
from StockBench.models.constants.simulation_results_constants import *


def ChartingProxyFunction(default_chart_filepaths: dict):
    """Decorator for a simulation proxy function. Wraps the simulation in a try block and catches any errors."""

    def decorator(charting_fxn: Callable):
        @wraps(charting_fxn)
        def wrapper(self, *args, **kwargs):
            try:
                return charting_fxn(self, *args, **kwargs)
            except ChartingError as e:
                message = f'Charting error: {e}'
            except Exception as e:
                message = f'Unexpected error: {type(e)} {e} {traceback.format_exc()}'

            default_chart_filepaths['status_code'] = 400
            default_chart_filepaths['message'] = message

            return default_chart_filepaths

        return wrapper

    return decorator


class ChartingProxy:
    """Proxy acting as a middle man between the controller and the charting engine. Allows us to wrap the proxy function
     to handle errors that the charting engines throw."""
    SINGULAR_DEFAULT_CHART_FILEPATHS = {
        OVERVIEW_CHART_FILEPATH_KEY: '',
        ACCOUNT_VALUE_LINE_CHART_FILEPATH_KEY: '',
        BUY_RULES_BAR_CHART_FILEPATH_KEY: '',
        SELL_RULES_BAR_CHART_FILEPATH_KEY: '',
        POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY: '',
        POSITIONS_PL_BAR_CHART_FILEPATH_KEY: '',
        POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH_KEY: '',
        POSITIONS_PLPC_BOX_PLOT_CHART_FILEPATH_KEY: ''
    }

    MULTI_DEFAULT_CHART_FILEPATHS = {
        OVERVIEW_CHART_FILEPATH_KEY: '',
        BUY_RULES_BAR_CHART_FILEPATH_KEY: '',
        SELL_RULES_BAR_CHART_FILEPATH_KEY: '',
        POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY: '',
        POSITIONS_PL_BAR_CHART_FILEPATH_KEY: '',
        POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH_KEY: '',
        POSITIONS_PLPC_BOX_PLOT_CHART_FILEPATH_KEY: ''
    }

    FOLDER_DEFAULT_CHART_FILEPATHS = {
        TRADES_MADE_BAR_CHART_FILEPATH_KEY: '',
        EFFECTIVENESS_BAR_CHART_FILEPATH_KEY: '',
        TOTAL_PL_BAR_CHART_FILEPATH_KEY: '',
        AVERAGE_PL_BAR_CHART_FILEPATH_KEY: '',
        MEDIAN_PL_BAR_CHART_FILEPATH_KEY: '',
        STDDEV_PL_BAR_CHART_FILEPATH_KEY: '',
        POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH_KEY: '',
        POSITIONS_PLPC_BOX_PLOT_CHART_FILEPATH_KEY: ''
    }

    def __init__(self, singular_charting_engine: SingularChartingEngine, multi_charting_engine: MultiChartingEngine,
                 folder_charting_engine: FolderChartingEngine):
        self.__singular_charting_engine = singular_charting_engine
        self.__multi_charting_engine = multi_charting_engine
        self.__folder_charting_engine = folder_charting_engine

    @ChartingProxyFunction(SINGULAR_DEFAULT_CHART_FILEPATHS)
    def build_singular_charts(self, simulation_results: dict, unique_chart_saving: bool, results_depth: int,
                              show_volume: bool) -> dict:
        """Proxy function for charting singular symbol simulation results with error capturing."""
        if unique_chart_saving:
            save_option = self.__singular_charting_engine.UNIQUE_SAVE
        else:
            save_option = self.__singular_charting_engine.TEMP_SAVE

        if results_depth == 0:
            return {
                OVERVIEW_CHART_FILEPATH_KEY: self.__singular_charting_engine.build_singular_overview_chart(
                    simulation_results[NORMALIZED_SIMULATION_DATA], simulation_results[SYMBOL_KEY],
                    simulation_results[AVAILABLE_INDICATORS], show_volume, save_option),
                ACCOUNT_VALUE_LINE_CHART_FILEPATH_KEY: self.__singular_charting_engine.build_account_value_line_chart(
                    simulation_results[NORMALIZED_SIMULATION_DATA][Simulator.ACCOUNT_VALUE_COLUMN_NAME].tolist(),
                    simulation_results[SYMBOL_KEY], save_option),
                BUY_RULES_BAR_CHART_FILEPATH_KEY: self.__singular_charting_engine.build_rules_bar_chart(
                    simulation_results[POSITIONS_KEY], BUY_SIDE, simulation_results[SYMBOL_KEY], save_option),
                SELL_RULES_BAR_CHART_FILEPATH_KEY: self.__singular_charting_engine.build_rules_bar_chart(
                    simulation_results[POSITIONS_KEY], SELL_SIDE, simulation_results[SYMBOL_KEY], save_option),
                POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY:
                    self.__singular_charting_engine.build_positions_duration_bar_chart(
                        simulation_results[POSITIONS_KEY], simulation_results[SYMBOL_KEY], save_option),
                POSITIONS_PL_BAR_CHART_FILEPATH_KEY:
                    self.__singular_charting_engine.build_positions_profit_loss_bar_chart(
                        simulation_results[POSITIONS_KEY], simulation_results[SYMBOL_KEY], save_option),
                POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH_KEY:
                    self.__singular_charting_engine.build_single_strategy_result_dataset_positions_plpc_histogram_chart(
                        simulation_results[POSITIONS_KEY], simulation_results[SYMBOL_KEY],
                        simulation_results[STRATEGY_KEY], save_option),
                POSITIONS_PLPC_BOX_PLOT_CHART_FILEPATH_KEY:
                    self.__singular_charting_engine.build_single_strategy_result_dataset_positions_plpc_box_plot(
                        simulation_results[POSITIONS_KEY], simulation_results[STRATEGY_KEY],
                        simulation_results[SYMBOL_KEY], save_option)
            }
        else:
            # user opted to only see data, no charts
            return ChartingProxy.SINGULAR_DEFAULT_CHART_FILEPATHS

    @ChartingProxyFunction(MULTI_DEFAULT_CHART_FILEPATHS)
    def build_multi_charts(self, simulation_results: dict, unique_chart_saving: bool, results_depth: int) -> dict:
        """Proxy function for charting multi-symbol simulation results with error capturing."""
        if unique_chart_saving:
            save_option = self.__multi_charting_engine.UNIQUE_SAVE
        else:
            save_option = self.__multi_charting_engine.TEMP_SAVE

        if results_depth == Simulator.CHARTS_AND_DATA:
            return {
                OVERVIEW_CHART_FILEPATH_KEY: MultiChartingEngine.build_multi_overview_chart(
                    simulation_results[INDIVIDUAL_RESULTS_KEY], simulation_results[INITIAL_ACCOUNT_VALUE_KEY],
                    save_option),
                BUY_RULES_BAR_CHART_FILEPATH_KEY: self.__multi_charting_engine.build_rules_bar_chart(
                    simulation_results[POSITIONS_KEY], BUY_SIDE, None, save_option),
                SELL_RULES_BAR_CHART_FILEPATH_KEY: self.__multi_charting_engine.build_rules_bar_chart(
                    simulation_results[POSITIONS_KEY], SELL_SIDE, None, save_option),
                POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY:
                    self.__multi_charting_engine.build_positions_duration_bar_chart(simulation_results[POSITIONS_KEY],
                                                                                    None, save_option),
                POSITIONS_PL_BAR_CHART_FILEPATH_KEY: self.__multi_charting_engine.build_positions_profit_loss_bar_chart(
                    simulation_results[POSITIONS_KEY], None, save_option),
                POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH_KEY:
                    self.__multi_charting_engine.build_single_strategy_result_dataset_positions_plpc_histogram_chart(
                        simulation_results[POSITIONS_KEY], simulation_results[STRATEGY_KEY], None, save_option),
                POSITIONS_PLPC_BOX_PLOT_CHART_FILEPATH_KEY:
                    self.__multi_charting_engine.build_single_strategy_result_dataset_positions_plpc_box_plot(
                        simulation_results[POSITIONS_KEY], simulation_results[STRATEGY_KEY], None, save_option)
            }
        else:
            # user opted to only see data, no charts
            return ChartingProxy.MULTI_DEFAULT_CHART_FILEPATHS

    @ChartingProxyFunction(FOLDER_DEFAULT_CHART_FILEPATHS)
    def build_folder_charts(self, simulation_results: list) -> dict:
        """Proxy function for charting folder simulation results with error capturing."""
        # NOTE: results depth is not an option for folder simulations
        return {
            TRADES_MADE_BAR_CHART_FILEPATH_KEY:
                self.__folder_charting_engine.build_trades_made_bar_chart(simulation_results),
            EFFECTIVENESS_BAR_CHART_FILEPATH_KEY:
                self.__folder_charting_engine.build_effectiveness_bar_chart(simulation_results),
            TOTAL_PL_BAR_CHART_FILEPATH_KEY: self.__folder_charting_engine.build_total_pl_bar_chart(simulation_results),
            AVERAGE_PL_BAR_CHART_FILEPATH_KEY:
                self.__folder_charting_engine.build_average_pl_bar_chart(simulation_results),
            MEDIAN_PL_BAR_CHART_FILEPATH_KEY:
                self.__folder_charting_engine.build_median_pl_bar_chart(simulation_results),
            STDDEV_PL_BAR_CHART_FILEPATH_KEY:
                self.__folder_charting_engine.build_stddev_pl_bar_chart(simulation_results),
            POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH_KEY:
                self.__folder_charting_engine.build_positions_plpc_histogram_chart(simulation_results),
            POSITIONS_PLPC_BOX_PLOT_CHART_FILEPATH_KEY:
                self.__folder_charting_engine.build_positions_plpc_box_chart(simulation_results)
        }
