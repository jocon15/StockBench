from plotly.subplots import make_subplots
import plotly.graph_objects as plotter
from typing import List, Tuple

from StockBench.charting.charting_engine import ChartingEngine
from StockBench.charting.display_constants import OFF_BLUE
from StockBench.constants import *


class FolderChartingEngine(ChartingEngine):
    """Charting tools for folder simulation analysis."""

    @staticmethod
    def build_trades_made_bar_chart(folder_results: List[dict]) -> str:
        """Build a bar chart for trades made.

        Args:
            folder_results: The results of the folder simulation.

        return:
            str: The filepath of the chart.
        """
        strategy_names, trades_made_data = FolderChartingEngine._extract_data_from_results(folder_results,
                                                                                           TRADES_MADE_KEY)

        formatted_fig = FolderChartingEngine._build_simple_bar_chart(strategy_names, trades_made_data,
                                                                     'Trades Made per Strategy', OFF_BLUE)

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, ChartingEngine.TEMP_SAVE,
                                                'temp_folder_trades_made', f'')

    @staticmethod
    def build_effectiveness_bar_chart(folder_results: List[dict]) -> str:
        """Build a bar chart for effectiveness.

        Args:
            folder_results: The results of the folder simulation.

        return:
            str: The filepath of the chart.
        """
        strategy_names, effectiveness_data = FolderChartingEngine._extract_data_from_results(folder_results,
                                                                                             EFFECTIVENESS_KEY)

        formatted_fig = FolderChartingEngine._build_simple_bar_chart(strategy_names, effectiveness_data,
                                                                     'Effectiveness % per Strategy', OFF_BLUE)

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, ChartingEngine.TEMP_SAVE,
                                                'temp_folder_effectiveness', f'')

    @staticmethod
    def build_total_pl_bar_chart(folder_results: List[dict]) -> str:
        """Build a bar chart for effectiveness.

        Args:
            folder_results: The results of the folder simulation.

        return:
            str: The filepath of the chart.
        """
        strategy_names, total_pl_data = FolderChartingEngine._extract_data_from_results(folder_results,
                                                                                        TOTAL_PROFIT_LOSS_KEY)

        formatted_fig = FolderChartingEngine._build_simple_bar_chart(strategy_names, total_pl_data,
                                                                     'Total P/L per Strategy', OFF_BLUE)

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, ChartingEngine.TEMP_SAVE,
                                                'temp_folder_total_pl', f'')

    @staticmethod
    def build_average_pl_bar_chart(folder_results: List[dict]) -> str:
        """Build a bar chart for average pl.

        Args:
            folder_results: The results of the folder simulation.

        return:
            str: The filepath of the chart.
        """
        strategy_names, average_pl_data = FolderChartingEngine._extract_data_from_results(folder_results,
                                                                                          AVERAGE_PROFIT_LOSS_KEY)

        formatted_fig = FolderChartingEngine._build_simple_bar_chart(strategy_names, average_pl_data,
                                                                     'Average P/L per Strategy', OFF_BLUE)

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, ChartingEngine.TEMP_SAVE,
                                                'temp_folder_average_pl', f'')

    @staticmethod
    def build_median_pl_bar_chart(folder_results: List[dict]) -> str:
        """Build a bar chart for average pl.

        Args:
            folder_results: The results of the folder simulation.

        return:
            str: The filepath of the chart.
        """
        strategy_names, median_pl_data = FolderChartingEngine._extract_data_from_results(folder_results,
                                                                                         MEDIAN_PROFIT_LOSS_KEY)

        formatted_fig = FolderChartingEngine._build_simple_bar_chart(strategy_names, median_pl_data,
                                                                     'Median P/L per Strategy', OFF_BLUE)

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, ChartingEngine.TEMP_SAVE,
                                                'temp_folder_median_pl', f'')

    @staticmethod
    def build_stddev_pl_bar_chart(folder_results: List[dict]) -> str:
        """Build a bar chart for average pl.

        Args:
            folder_results: The results of the folder simulation.

        return:
            str: The filepath of the chart.
        """
        strategy_names, stddev_pl_data = FolderChartingEngine._extract_data_from_results(
            folder_results, STANDARD_PROFIT_LOSS_DEVIATION_KEY)

        formatted_fig = FolderChartingEngine._build_simple_bar_chart(strategy_names, stddev_pl_data,
                                                                     'Standard Deviation (P) P/L per Strategy',
                                                                     OFF_BLUE)

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, ChartingEngine.TEMP_SAVE,
                                                'temp_folder_stddev_pl', f'')

    @staticmethod
    def build_positions_histogram_chart(folder_results: List[dict]) -> str:
        """Build a bar chart for average pl.

        Args:
            folder_results: The results of the folder simulation.

        return:
            str: The filepath of the chart.
        """
        strategy_names = []
        positions_data = []
        for result in folder_results:
            strategy_names.append(result[STRATEGY_KEY])
            data_list = []
            for position in result[POSITIONS_KEY]:
                data_list.append(position.lifetime_profit_loss())
            positions_data.append(data_list)

        formatted_fig = ChartingEngine._build_multi_dataset_histogram(
            strategy_names, positions_data, 'Position Profit/Loss % Distribution per Strategy')

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, ChartingEngine.TEMP_SAVE,
                                                'temp_positions_histogram_chart', f'')

    @staticmethod
    def _extract_data_from_results(results: List[dict], data_key: str) -> Tuple[List, List]:
        """Extract strategy and data values from folder results.

        Args:
            results: The results of the folder simulation.
            data_key: The key of the data to extract.

        return:
            tuple: The list of strategy names and the list of data values.
        """
        strategy_names = []
        data_values = []
        for result in results:
            strategy_names.append(result[STRATEGY_KEY])
            data_values.append(float(result[data_key]))

        return strategy_names, data_values

    @staticmethod
    def _build_simple_bar_chart(x_values: list, y_values: list, title: str, marker_color: str) -> str:
        """Build a simple bar chart.

        Args:
            x_values: The x values of the bar chart.
            y_values: The y values of the bar chart.
            title: The title of the bar chart.
            marker_color: The bar color.

        return:
            str: The formatted figure.
        """
        rows = 1
        cols = 1

        chart_list = [[{"type": "bar"}]]
        chart_titles = (title,)

        # Parent Plot
        fig = make_subplots(rows=rows, cols=cols, shared_xaxes=True, vertical_spacing=0.15, horizontal_spacing=0.05,
                            specs=chart_list, subplot_titles=chart_titles)

        # rule counts chart
        fig.add_trace(plotter.Bar(
            x=x_values,
            y=y_values,
            marker=dict(color=marker_color), name='Count'), 1, 1)

        # set the layout
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False)

        # format the chart (remove plotly white border)
        return ChartingEngine.format_chart(fig)
