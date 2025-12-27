from typing import List, Tuple
import plotly.graph_objects as plotter

from StockBench.controllers.charting.charting_engine import ChartingEngine
from StockBench.controllers.charting.display_constants import OFF_BLUE
from StockBench.models.constants.simulation_results_constants import *


class FolderChartingEngine(ChartingEngine):
    """Charting tools for folder simulation analysis.

    NOTE: these functions do not log because folder simulations use multiple progress observers. If they were to log,
    the log message would be repeated for as many strategies that were being simulated, which is bad. Instead, logging
    is done on a single progress observer by the stockbench controller.
    """

    def __init__(self, identifier: int):
        super().__init__(identifier)

    @staticmethod
    def build_trades_made_bar_chart(results: List[dict]) -> str:
        """Builds a bar chart for trades made."""
        strategy_names, trades_made_data = (
            FolderChartingEngine.__extract_values_from_results_by_key(results, TRADES_MADE_KEY))

        return FolderChartingEngine.__build_bar_chart(strategy_names, trades_made_data,
                                                      'Trades Made per Strategy', OFF_BLUE,
                                                      'temp_folder_trades_made')

    @staticmethod
    def build_effectiveness_bar_chart(results: List[dict]) -> str:
        """Builds a bar chart for effectiveness."""
        strategy_names, effectiveness_data = (
            FolderChartingEngine.__extract_values_from_results_by_key(results, EFFECTIVENESS_KEY))

        return FolderChartingEngine.__build_bar_chart(strategy_names, effectiveness_data,
                                                      'Effectiveness % per Strategy', OFF_BLUE,
                                                      'temp_folder_effectiveness')

    @staticmethod
    def build_total_pl_bar_chart(results: List[dict]) -> str:
        """Builds a bar chart for effectiveness."""
        strategy_names, total_pl_data = (
            FolderChartingEngine.__extract_values_from_results_by_key(results, TOTAL_PL_KEY))

        return FolderChartingEngine.__build_bar_chart(strategy_names, total_pl_data, 'Total P/L per Strategy',
                                                      OFF_BLUE, 'temp_folder_total_pl')

    @staticmethod
    def build_average_pl_bar_chart(results: List[dict]) -> str:
        """Builds a bar chart for average pl."""
        strategy_names, average_pl_data = (
            FolderChartingEngine.__extract_values_from_results_by_key(results, AVERAGE_PL_KEY))

        return FolderChartingEngine.__build_bar_chart(strategy_names, average_pl_data,
                                                      'Average P/L per Strategy', OFF_BLUE,
                                                      'temp_folder_average_pl')

    @staticmethod
    def build_median_pl_bar_chart(results: List[dict]) -> str:
        """Builds a bar chart for median pl."""
        strategy_names, median_pl_data = (
            FolderChartingEngine.__extract_values_from_results_by_key(results, MEDIAN_PL_KEY))

        return FolderChartingEngine.__build_bar_chart(strategy_names, median_pl_data,
                                                      'Median P/L per Strategy', OFF_BLUE,
                                                      'temp_folder_median_pl')

    @staticmethod
    def build_stddev_pl_bar_chart(results: List[dict]) -> str:
        """Build a bar chart for stddev pl."""
        strategy_names, stddev_pl_data = (
            FolderChartingEngine.__extract_values_from_results_by_key(results, STANDARD_DEVIATION_PL_KEY))

        return FolderChartingEngine.__build_bar_chart(strategy_names, stddev_pl_data,
                                                      'Standard Deviation (P) P/L per Strategy', OFF_BLUE,
                                                      'temp_folder_stddev_pl')

    @staticmethod
    def build_positions_plpc_histogram_chart(results: List[dict]) -> str:
        """Build a histogram chart for position plpc."""
        strategy_names = []
        positions_data = []
        for result in results:
            strategy_names.append(result[STRATEGY_KEY])
            positions_data.append([position.lifetime_profit_loss_percent() for position in result[POSITIONS_KEY]])

        formatted_fig = ChartingEngine._build_multiple_strategy_result_dataset_histogram(
            strategy_names, positions_data, 'Position Profit/Loss % Distribution per Strategy')

        return ChartingEngine.handle_save_chart(formatted_fig, ChartingEngine.TEMP_SAVE,
                                                'temp_positions_histogram_chart', f'')

    @staticmethod
    def build_positions_plpc_box_chart(results: List[dict]) -> str:
        """Build a box and whisker chart for position plpc."""
        strategy_names = []
        positions_data = []
        for result in results:
            strategy_names.append(result[STRATEGY_KEY])
            positions_data.append([position.lifetime_profit_loss_percent() for position in result[POSITIONS_KEY]])

        formatted_fig = ChartingEngine._build_multiple_strategy_result_dataset_box_plot(
            strategy_names, positions_data, 'Position Profit/Loss % Distribution per Strategy')

        return ChartingEngine.handle_save_chart(formatted_fig, ChartingEngine.TEMP_SAVE,
                                                'temp_positions_box_chart', f'')

    @staticmethod
    def __extract_values_from_results_by_key(results: List[dict], key: str) -> Tuple[List[str], List[float]]:
        """Extract strategy names and values by key from folder results."""
        strategy_names = [result[STRATEGY_KEY] for result in results]
        data_values = [float(result[key]) for result in results]

        return strategy_names, data_values

    @staticmethod
    def __build_bar_chart(x_values: list, y_values: list, title: str, marker_color: str,
                          temp_filename: str) -> str:
        """Builds a generic bar chart."""
        fig = plotter.Figure(plotter.Bar(x=x_values, y=y_values, marker=dict(color=marker_color), name='Count'))

        fig.update_layout(template=ChartingEngine.PLOTLY_THEME, xaxis_rangeslider_visible=False, title=title,
                          title_x=0.5)

        formatted_fig = ChartingEngine.format_chart(fig)

        return ChartingEngine.handle_save_chart(formatted_fig, ChartingEngine.TEMP_SAVE, temp_filename, '')
