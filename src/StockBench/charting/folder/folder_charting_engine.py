from plotly.subplots import make_subplots
import plotly.graph_objects as plotter
from StockBench.charting.charting_engine import ChartingEngine
from StockBench.charting.display_constants import *


class FolderChartingEngine(ChartingEngine):
    """Charting engine for folder charts."""

    @staticmethod
    def build_trades_made_chart(folder_results: list) -> str:
        """Build a chart for trades made."""
        strategy_names = []
        trades_made_data = []
        for result in folder_results:
            strategy_names.append(result['strategy'])
            trades_made_data.append(float(result['trades_made']))

        formatted_fig = FolderChartingEngine._build_simple_bar_chart(strategy_names, trades_made_data,
                                                                     'Trades Made per Strategy', OFF_BLUE)

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, ChartingEngine.TEMP_SAVE,
                                                'temp_folder_trades_made', f'')

    @staticmethod
    def build_effectiveness_chart(folder_results: list) -> str:
        """Build a chart for effectiveness."""
        strategy_names = []
        trades_made_data = []
        for result in folder_results:
            strategy_names.append(result['strategy'])
            trades_made_data.append(float(result['effectiveness']))

        formatted_fig = FolderChartingEngine._build_simple_bar_chart(strategy_names, trades_made_data,
                                                                     'Effectiveness % per Strategy', OFF_BLUE)

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, ChartingEngine.TEMP_SAVE,
                                                'temp_folder_effectiveness', f'')

    @staticmethod
    def build_average_pl_chart(folder_results: list) -> str:
        """Build a chart for average pl."""
        strategy_names = []
        trades_made_data = []
        for result in folder_results:
            strategy_names.append(result['strategy'])
            trades_made_data.append(float(result['average_profit_loss']))

        formatted_fig = FolderChartingEngine._build_simple_bar_chart(strategy_names, trades_made_data,
                                                                     'Average P/L per Strategy', OFF_BLUE)

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, ChartingEngine.TEMP_SAVE,
                                                'temp_folder_average_pl', f'')

    @staticmethod
    def _build_simple_bar_chart(x_values: list, y_values: list, title: str, marker_color: str) -> str:
        """Build a simple bar chart."""
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
