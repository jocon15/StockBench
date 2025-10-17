import traceback
from typing import Callable

from StockBench.controllers.charting.charting_engine import ChartingEngine
from StockBench.controllers.charting.exceptions import ChartingError
from StockBench.controllers.charting.singular.singular_charting_engine import SingularChartingEngine
from StockBench.controllers.simulator.simulator import Simulator
from StockBench.models.constants.chart_filepath_key_constants import *
from StockBench.models.constants.general_constants import BUY_SIDE, SELL_SIDE
from StockBench.models.constants.simulation_results_constants import *


def ChartingProxyFunction(default_chart_filepaths: dict):
    """Decorator for a simulation proxy function. Wraps the simulation in a try block and catches any errors."""

    def decorator(charting_fxn: Callable):
        def wrapper(*args, **kwargs):
            try:
                return charting_fxn(*args, **kwargs)
            except ChartingError as e:
                message = f'Charting error: {e}'
            except Exception as e:
                message = f'Unexpected error: {type(e)} {e} {traceback.print_exc()}'

            default_chart_filepaths['status_code'] = 400
            default_chart_filepaths['message'] = message

            return default_chart_filepaths
        return wrapper
    return decorator


class ChartingProxy:
    """"""
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

    @staticmethod
    @ChartingProxyFunction(SINGULAR_DEFAULT_CHART_FILEPATHS)
    def build_singular_charts(simulation_results: dict, unique_chart_saving: bool, results_depth: int,
                              show_volume: bool) -> dict:
        """"""
        if unique_chart_saving:
            save_option = ChartingEngine.UNIQUE_SAVE
        else:
            save_option = ChartingEngine.TEMP_SAVE

        if results_depth == 0:
            return {
                OVERVIEW_CHART_FILEPATH_KEY: SingularChartingEngine.build_singular_overview_chart(
                    simulation_results[NORMALIZED_SIMULATION_DATA], simulation_results[SYMBOL_KEY],
                    simulation_results[AVAILABLE_INDICATORS], show_volume, save_option),
                ACCOUNT_VALUE_LINE_CHART_FILEPATH_KEY: SingularChartingEngine.build_account_value_line_chart(
                    simulation_results[NORMALIZED_SIMULATION_DATA][Simulator.ACCOUNT_VALUE_COLUMN_NAME].tolist(),
                    simulation_results[SYMBOL_KEY], save_option),
                BUY_RULES_BAR_CHART_FILEPATH_KEY: ChartingEngine.build_rules_bar_chart(
                    simulation_results[POSITIONS_KEY], BUY_SIDE, simulation_results[SYMBOL_KEY], save_option),
                SELL_RULES_BAR_CHART_FILEPATH_KEY: ChartingEngine.build_rules_bar_chart(
                    simulation_results[POSITIONS_KEY], SELL_SIDE, simulation_results[SYMBOL_KEY], save_option),
                POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY: ChartingEngine.build_positions_duration_bar_chart(
                    simulation_results[POSITIONS_KEY], simulation_results[SYMBOL_KEY], save_option),
                POSITIONS_PL_BAR_CHART_FILEPATH_KEY: ChartingEngine.build_positions_profit_loss_bar_chart(
                    simulation_results[POSITIONS_KEY], simulation_results[SYMBOL_KEY], save_option),
                POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH_KEY:
                    SingularChartingEngine.build_single_strategy_result_dataset_positions_plpc_histogram_chart(
                        simulation_results[POSITIONS_KEY], simulation_results[SYMBOL_KEY],
                        simulation_results[STRATEGY_KEY], save_option),
                POSITIONS_PLPC_BOX_PLOT_CHART_FILEPATH_KEY:
                    SingularChartingEngine.build_single_strategy_result_dataset_positions_plpc_box_plot(
                        simulation_results[POSITIONS_KEY], simulation_results[STRATEGY_KEY],
                        simulation_results[SYMBOL_KEY], save_option)
            }
        else:
            # user opted to only see data, no charts
            return ChartingProxy.SINGULAR_DEFAULT_CHART_FILEPATHS
