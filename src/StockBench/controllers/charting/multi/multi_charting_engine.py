import statistics
from typing import List

import pandas as pd
from plotly.graph_objs import Bar, Indicator
import plotly.graph_objects as plotter
from plotly.subplots import make_subplots

from StockBench.controllers.charting.display_constants import *
from StockBench.controllers.charting.charting_engine import ChartingEngine
from StockBench.models.constants.simulation_results_constants import *


class MultiChartingEngine(ChartingEngine):
    """Charting tools for multiple simulation analysis."""

    def __init__(self, identifier: int):
        super().__init__(identifier)

    def build_multi_overview_chart(self, results: List[dict], initial_balance: float,
                                   save_option: int = ChartingEngine.TEMP_SAVE) -> str:
        """Builds the multi overview chart consisting of OHLC, volume, and other indicators."""
        self.gui_status_log.info('Building overview chart...')
        rows = 2
        cols = 2

        chart_list = [[{"type": "bar"}, {"type": "indicator"}], [{"type": "bar"}, {"type": "indicator"}]]
        chart_titles = ('Total Profit/Loss per Symbol ($)', '', 'Trades Made per Symbol', '')

        fig = make_subplots(rows=rows,
                            cols=cols,
                            shared_xaxes=True,
                            vertical_spacing=0.15,
                            horizontal_spacing=0.05,
                            specs=chart_list,
                            subplot_titles=chart_titles)

        fig.add_trace(MultiChartingEngine.__build_overview_profit_loss_bar_subplot(results), row=1, col=1)
        fig.add_trace(MultiChartingEngine.__overview_avg_effectiveness_gauge_subplot(results), row=1, col=2)
        fig.add_trace(MultiChartingEngine.__build_overview_trades_made_bar_subplot(results), row=2, col=1)
        fig.add_trace(MultiChartingEngine.__overview_avg_profit_loss_gauge(results, initial_balance), row=2, col=2)

        fig.update_layout(template=self.PLOTLY_THEME, title=f'Simulation Results for {len(results)} Symbols',
                          xaxis_rangeslider_visible=False, showlegend=False)

        formatted_fig = ChartingEngine.format_chart(fig)

        return ChartingEngine.handle_save_chart(formatted_fig, save_option, 'temp_overview_chart', 'multi')

    @staticmethod
    def __build_overview_profit_loss_bar_subplot(results: List[dict]) -> Bar:
        """Builds an overview profit/loss bar subplot."""
        color_df = pd.DataFrame()
        bar_colors = []
        for value in MultiChartingEngine.__get_total_pl_per_symbol_from_results(results):
            if value > 0:
                bar_colors.append(BULL_GREEN)
            else:
                bar_colors.append(BEAR_RED)
        color_df['colors'] = bar_colors

        return plotter.Bar(
            x=MultiChartingEngine.__get_symbols_from_results(results),
            y=MultiChartingEngine.__get_total_pl_per_symbol_from_results(results),
            marker_color=color_df['colors'],
            name='PL'
        )

    @staticmethod
    def __overview_avg_effectiveness_gauge_subplot(results: List[dict]) -> Indicator:
        """Builds an overview average effectiveness gauge subplot."""
        indicator_value = MultiChartingEngine.__calculate_avg_effectiveness_from_results(results)

        bar_color = MultiChartingEngine.__get_gauge_bar_color_by_value(indicator_value, 50.0)

        return plotter.Indicator(
            domain={'x': [0, 1], 'y': [0, 1]},
            value=indicator_value,
            number={"font": {"size": 55}},
            mode="gauge+number",
            title={'text': "Average Effectiveness Across all Trades (%)"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': bar_color},
                   'steps': [
                       {'range': [0, 50], 'color': PLOTLY_DARK_BACKGROUND},
                       {'range': [50, 100], 'color': PLOTLY_DARK_BACKGROUND}]})

    @staticmethod
    def __overview_avg_profit_loss_gauge(results: List[dict], initial_balance: float) -> Indicator:
        """Builds an overview average profit/loss gauge subplot."""
        indicator_value = MultiChartingEngine.__calculate_avg_pl_from_results(results)
        upper_bound = initial_balance
        lower_bound = -initial_balance

        bar_color = MultiChartingEngine.__get_gauge_bar_color_by_value(indicator_value, 0.0)

        return plotter.Indicator(
            domain={'x': [0, 1], 'y': [0, 1]},
            value=indicator_value,
            number={"font": {"size": 55}},
            mode="gauge+number",
            title={'text': "Average Total Profit/Loss per Symbol ($)"},
            gauge={'axis': {'range': [lower_bound, upper_bound]},
                   'bar': {'color': bar_color},
                   'steps': [
                       {'range': [lower_bound, 0], 'color': PLOTLY_DARK_BACKGROUND},
                       {'range': [0, upper_bound], 'color': PLOTLY_DARK_BACKGROUND}]})

    @staticmethod
    def __build_overview_trades_made_bar_subplot(results: List[dict]) -> Bar:
        """Builds an overview trades made bar chart subplot."""
        return plotter.Bar(
            x=MultiChartingEngine.__get_symbols_from_results(results),
            y=MultiChartingEngine.__get_trades_made_per_symbol_from_results(results),
            marker=dict(color=OFF_BLUE))

    @staticmethod
    def __get_symbols_from_results(results: List[dict]) -> list:
        """Gets a list of symbols from the results list."""
        return MultiChartingEngine.__extract_values_from_results_by_key(SYMBOL_KEY, results)

    @staticmethod
    def __get_total_pl_per_symbol_from_results(results: List[dict]) -> list:
        """Gets a list of total profit/loss from the results list."""
        return MultiChartingEngine.__extract_values_from_results_by_key(TOTAL_PL_KEY, results)

    @staticmethod
    def __get_trades_made_per_symbol_from_results(results: List[dict]) -> list:
        """Gets a list of trades made from the results list."""
        return MultiChartingEngine.__extract_values_from_results_by_key(TRADES_MADE_KEY, results)

    @staticmethod
    def __calculate_avg_effectiveness_from_results(results: List[dict]) -> float:
        """Calculate average effectiveness from the results list."""
        effectiveness_per_symbol = MultiChartingEngine.__extract_values_from_results_by_key(EFFECTIVENESS_KEY, results)
        return round(float(statistics.mean(effectiveness_per_symbol)), 2)

    @staticmethod
    def __calculate_avg_pl_from_results(results: List[dict]) -> float:
        """Calculates the average profit/loss from the results list."""
        pl_per_symbol = MultiChartingEngine.__extract_values_from_results_by_key(TOTAL_PL_KEY, results)
        return round(float(statistics.mean(pl_per_symbol)), 2)

    @staticmethod
    def __extract_values_from_results_by_key(key: str, results: List[dict]) -> list:
        """Builds a list of values from each result based on a given key."""
        return [stock[key] for stock in results]

    @staticmethod
    def __get_gauge_bar_color_by_value(value: float, threshold: float) -> str:
        """Get gauge bar color based on a value and a threshold."""
        if value > threshold:
            return 'green'
        return 'red'
