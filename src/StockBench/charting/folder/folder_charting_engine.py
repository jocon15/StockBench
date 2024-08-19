from plotly.subplots import make_subplots
import plotly.graph_objects as plotter
from StockBench.charting.charting_engine import ChartingEngine
from StockBench.charting.display_constants import *


class FolderChartingEngine(ChartingEngine):
    """Charting engine for folder charts."""

    @staticmethod
    def build_trades_made_chart(folder_results: list) -> str:
        """Build a chart for trades made."""
        rows = 2
        cols = 1

        chart_list = [[{"type": "bar"}], [{"type": "bar"}]]
        chart_titles = ('Trades Made per Strategy',)

        # Parent Plot
        fig = make_subplots(rows=rows,
                            cols=cols,
                            shared_xaxes=True,
                            vertical_spacing=0.15,
                            horizontal_spacing=0.05,
                            specs=chart_list,
                            subplot_titles=chart_titles)

        strategy_names = []
        trades_made_data = []
        for result in folder_results:
            strategy_names.append(result['strategy'])
            trades_made_data.append(float(result['trades_made']))

        # rule counts chart
        fig.add_trace(plotter.Bar(
            x=strategy_names,
            y=trades_made_data,
            marker=dict(color=OFF_BLUE), name='Count'), 1, 1)

        # set the layout
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False)

        # format the chart (remove plotly white border)
        formatted_fig = ChartingEngine.format_chart(fig)

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, ChartingEngine.TEMP_SAVE, 'temp_folder_trades_made', f'')
