import os
import statistics
import numpy as np
import pandas as pd
from typing import Optional, List, Union
import plotly.offline as offline
import plotly.graph_objects as plotter
from plotly.graph_objs import Bar, Scatter, Figure
from plotly.subplots import make_subplots
from plotly.figure_factory import create_distplot

from StockBench.charting.display_constants import *
from StockBench.function_tools.timestamp import datetime_timestamp
from StockBench.constants import *
from StockBench.position.position import Position


class ChartingEngine:
    """Base class for a charting engine."""

    TEMP_SAVE = 0
    UNIQUE_SAVE = 1

    PLOTLY_CHART_MARGIN_TOP = 50
    PLOTLY_CHART_MARGIN_BOTTOM = 60
    PLOTLY_CHART_MARGIN_LEFT = 60
    PLOTLY_CHART_MARGIN_RIGHT = 100

    @staticmethod
    def build_rules_bar_chart(positions: list, side: str, symbol: Optional[str], save_option: int = TEMP_SAVE) -> str:
        """Builds a subplot chart for rule analysis of a given side."""
        rows = 2
        cols = 1

        side_title = ChartingEngine.__translate_position_title_from_side(side)

        chart_list = [[{"type": "bar"}], [{"type": "bar"}]]
        chart_titles = (f'{side_title} Count per Rule', f'Position Profit/Loss % Analytics per {side_title} Rule')

        fig = make_subplots(rows=rows,
                            cols=cols,
                            shared_xaxes=True,
                            vertical_spacing=0.15,
                            horizontal_spacing=0.05,
                            specs=chart_list,
                            subplot_titles=chart_titles)

        fig.add_trace(ChartingEngine._build_rule_count_bar_trace(positions, side), 1, 1)

        rule_stats_traces = ChartingEngine._build_rule_stats_traces(positions, side)
        fig.add_trace(rule_stats_traces[0], 2, 1)
        fig.add_trace(rule_stats_traces[1], 2, 1)
        fig.add_trace(rule_stats_traces[2], 2, 1)

        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False)

        # format the chart (remove plotly white border)
        formatted_fig = ChartingEngine.format_chart(fig)

        temp_filename = f'temp_{side}_chart'
        if symbol:
            unique_prefix = f'{symbol}_{side}_rules_bar_chart'
        else:
            unique_prefix = f'multi_{side}_rules_bar_chart'

        return ChartingEngine.handle_save_chart(formatted_fig, save_option, temp_filename, unique_prefix)

    @staticmethod
    def build_positions_duration_bar_chart(positions: list, symbol: Optional[str], save_option: int = TEMP_SAVE) -> str:
        """Builds a bar chart for position duration analysis."""
        rows = 1
        cols = 1

        chart_list = [[{"type": "bar"}]]
        chart_titles = ('Duration per Position',)

        fig = make_subplots(rows=rows,
                            cols=cols,
                            shared_xaxes=True,
                            vertical_spacing=0.15,
                            horizontal_spacing=0.05,
                            specs=chart_list,
                            subplot_titles=chart_titles)

        position_analysis_traces = ChartingEngine._build_positions_duration_bar_traces(positions)
        fig.add_trace(position_analysis_traces[0], 1, 1)
        fig.add_trace(position_analysis_traces[1], 1, 1)
        fig.add_trace(position_analysis_traces[2], 1, 1)

        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, xaxis_title='Position',
                          yaxis_title='Duration (days)')

        # format the chart (remove plotly white border)
        formatted_fig = ChartingEngine.format_chart(fig)

        temp_filename = 'temp_positions_duration_bar_chart'
        if symbol:
            unique_prefix = f'{symbol}_positions_duration_bar_chart'
        else:
            unique_prefix = 'multi_positions_duration_bar_chart'

        return ChartingEngine.handle_save_chart(formatted_fig, save_option, temp_filename, unique_prefix)

    @staticmethod
    def build_positions_profit_loss_bar_chart(positions: list, symbol: Optional[str],
                                              save_option: int = TEMP_SAVE) -> str:
        """Builds a bar chart for profit/loss analysis of positions."""
        rows = 1
        cols = 1

        chart_list = [[{"type": "bar"}]]
        chart_titles = ('Total Profit/Loss per Position',)

        fig = make_subplots(rows=rows,
                            cols=cols,
                            shared_xaxes=True,
                            vertical_spacing=0.15,
                            horizontal_spacing=0.05,
                            specs=chart_list,
                            subplot_titles=chart_titles)

        position_analysis_traces = ChartingEngine._build_positions_total_pl_bar_traces(positions)
        fig.add_trace(position_analysis_traces[0], 1, 1)
        fig.add_trace(position_analysis_traces[1], 1, 1)
        fig.add_trace(position_analysis_traces[2], 1, 1)

        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, xaxis_title='Position',
                          yaxis_title='Profit/Loss ($)')

        # format the chart (remove plotly white border)
        formatted_fig = ChartingEngine.format_chart(fig)

        temp_filename = 'temp_positions_profit_loss_bar_chart'
        if symbol:
            unique_prefix = f'{symbol}_positions_profit_loss_bar_chart'
        else:
            unique_prefix = 'multi_positions_profit_loss_bar_chart'

        return ChartingEngine.handle_save_chart(formatted_fig, save_option, temp_filename, unique_prefix)

    @staticmethod
    def build_single_strategy_result_dataset_positions_plpc_histogram_chart(positions: List[Position],
                                                                            strategy_name: str,
                                                                            symbol: Optional[str],
                                                                            save_option=TEMP_SAVE) -> str:
        """Builds a histogram chart for positions profit/loss percent from a single strategy result dataset."""
        # formatting a single data set inside a list in order to use the multi data set histogram builder
        # (it will just build 1 histogram)
        strategy_names = [strategy_name]
        positions_data = [[position.lifetime_profit_loss_percent() for position in positions]]

        formatted_fig = ChartingEngine._build_multiple_strategy_result_dataset_histogram(strategy_names, positions_data,
                                                                                         'Position Profit/Loss % '
                                                                                         'Distribution')

        temp_filename = 'temp_positions_profit_loss_histogram_chart'
        if symbol:
            unique_prefix = f'{symbol}_positions_profit_loss_histogram_chart'
        else:
            unique_prefix = 'multi_positions_profit_loss_histogram_chart'

        return ChartingEngine.handle_save_chart(formatted_fig, save_option, temp_filename, unique_prefix)

    @staticmethod
    def build_single_strategy_result_dataset_positions_plpc_box_plot(positions: List[Position], strategy_name: str,
                                                                     symbol: Optional[str],
                                                                     save_option=TEMP_SAVE) -> str:
        """Builds a box and whisker chart for positions profit/loss percent."""
        # formatting a single data set inside a list in order to use the multi data set histogram builder
        # (it will just build 1 histogram)
        strategy_names = [strategy_name]
        positions_data = [[position.lifetime_profit_loss_percent() for position in positions]]

        formatted_fig = ChartingEngine._build_multiple_strategy_result_dataset_box_plot(strategy_names, positions_data,
                                                                                        'Position Profit/Loss % '
                                                                                        'Distribution')

        temp_filename = 'temp_positions_profit_loss_box_chart'
        if symbol:
            unique_prefix = f'{symbol}_positions_profit_loss_box_chart'
        else:
            unique_prefix = 'multi_positions_profit_loss_box_chart'

        return ChartingEngine.handle_save_chart(formatted_fig, save_option, temp_filename, unique_prefix)

    @staticmethod
    def handle_save_chart(formatted_fig: str, save_option: int, temp_filename: str, unique_prefix: str) -> str:
        """Handles chart saving based on chart save option."""
        if save_option == ChartingEngine.TEMP_SAVE:
            # save chart as temporary file - will be overwritten by any new chart
            chart_filepath = ChartingEngine.__save_chart(formatted_fig, f'{temp_filename}.html')
        elif save_option == ChartingEngine.UNIQUE_SAVE:
            # save chart as unique file for persistent saving
            chart_filepath = ChartingEngine.__save_chart(formatted_fig, f'{unique_prefix}_{datetime_timestamp()}.html')
        else:
            # no chart was saved
            chart_filepath = ''

        return chart_filepath

    @staticmethod
    def format_chart(fig: Figure):
        config = dict({
            'scrollZoom': False,
            'displayModeBar': False,
            'editable': False
        })

        plot_div = offline.plot(fig, config=config, output_type='div')

        formatted_fig = """
                                        <head>
                                        <body style="background-color:#111111;">
                                        </head>
                                        <body>
                                        {plot_div:s}
                                        </body>""".format(plot_div=plot_div)

        return formatted_fig

    @staticmethod
    def _build_rule_count_bar_trace(positions: List[Position], side: str) -> Bar:
        """Builds a bar trace for number of trades made for each rule."""
        stats = ChartingEngine.__get_rule_statistics(positions, side)

        df = pd.DataFrame()
        df['Rule'] = [key for key in stats.keys()]
        df['Count'] = [stats[key]['count'] for key in stats.keys()]

        return plotter.Bar(
            x=df['Rule'],
            y=df['Count'],
            width=0.2,
            marker=dict(color=OFF_BLUE), name='Count')

    @staticmethod
    def _build_rule_stats_traces(positions: List[Position], side: str) -> List[Bar]:
        """Builds a list of traces for algorithm rule analysis."""
        rule_stats = ChartingEngine.__get_rule_statistics(positions, side)

        df = pd.DataFrame()
        df['Rule'] = [key for key in rule_stats.keys()]
        df['Avg'] = [rule_stats[key]['average_plpc'] for key in rule_stats.keys()]
        df['Med'] = [rule_stats[key]['median_plpc'] for key in rule_stats.keys()]
        df['Stddev'] = [rule_stats[key]['stddev_plpc'] for key in rule_stats.keys()]

        return [plotter.Bar(x=df['Rule'], y=df['Avg'], width=0.2, marker=dict(color=AVG_COLOR), name='Mean'),
                plotter.Bar(x=df['Rule'], y=df['Med'], width=0.2, marker=dict(color=MED_COLOR), name='Median'),
                plotter.Bar(x=df['Rule'], y=df['Stddev'], width=0.2, marker=dict(color=STDDEV_COLOR), name='Stddev')]

    @staticmethod
    def _build_positions_duration_bar_traces(positions: List[Position]) -> List[Union[Bar, Scatter]]:
        """Builds a list of traces for position duration bar chart analysis."""
        durations = [position.duration() for position in positions]

        df = pd.DataFrame()
        df['duration'] = durations

        mean_values = [statistics.mean(durations) for _ in durations]
        median_values = [statistics.median(durations) for _ in durations]

        return [plotter.Bar(y=df['duration'], name='Duration'),
                plotter.Scatter(y=mean_values, marker=dict(color=MED_COLOR), name='Mean', mode='lines'),
                plotter.Scatter(y=median_values, marker=dict(color=STDDEV_COLOR), name='Median', mode='lines')]

    @staticmethod
    def _build_positions_total_pl_bar_traces(positions: List[Position]) -> List[Union[Bar, Scatter]]:
        """Builds a list of traces for position total profit/loss bar chart analysis."""
        total_pls = [position.lifetime_profit_loss() for position in positions]

        df = pd.DataFrame()
        df['total_pl'] = total_pls
        df['color'] = np.where(df['total_pl'] < 0, BEAR_RED, BULL_GREEN)

        mean_values = [statistics.mean(total_pls) for _ in total_pls]
        median_values = [statistics.median(total_pls) for _ in total_pls]

        return [plotter.Bar(y=df['total_pl'], marker_color=df['color'], name='Profit/Loss'),
                plotter.Scatter(y=mean_values, marker=dict(color=MED_COLOR), name='Mean', mode='lines'),
                plotter.Scatter(y=median_values, marker=dict(color=STDDEV_COLOR), name='Median', mode='lines')]

    @staticmethod
    def _build_multiple_strategy_result_dataset_histogram(strategy_names: list, positions_data: list,
                                                          title: str) -> str:
        """Build a histogram chart with multiple strategy datasets."""
        fig = create_distplot(positions_data, strategy_names, bin_size=0.1)

        fig.update_layout(xaxis=dict(
            zeroline=True,  # Enable the zero line
            zerolinewidth=1,  # Adjust line width
            zerolinecolor='#283442'),  # Customize color
            template='plotly_dark', xaxis_rangeslider_visible=False, title=title, title_x=0.5)

        return ChartingEngine.format_chart(fig)

    @staticmethod
    def _build_multiple_strategy_result_dataset_box_plot(strategy_names: list, positions_data: list,
                                                         title: str) -> str:
        """Build a box and whisker chart with multiple strategy datasets."""
        fig = plotter.Figure()

        for index, strategy_name in enumerate(strategy_names):
            fig.add_trace(plotter.Box(x=positions_data[index], name=strategy_name))

        fig.update_layout(xaxis=dict(
            zeroline=True,  # Enable the zero line
            zerolinewidth=1,  # Adjust line width
            zerolinecolor='#283442'),  # Customize color
            template='plotly_dark', xaxis_rangeslider_visible=False, title=title, title_x=0.5)

        return ChartingEngine.format_chart(fig)

    @staticmethod
    def __get_rule_statistics(positions: List[Position], side: str) -> dict:
        """Builds a dict of statistics for each rule based for the given side."""
        rule_stats = {}
        for position in positions:
            rule = ChartingEngine.__get_rule_from_side(position, side)

            rule_stats[rule] = {
                'count': ChartingEngine.__calculate_rule_count(positions, side, rule),
                'average_plpc': ChartingEngine.__calculate_average_plpc(positions, side, rule),
                'median_plpc': ChartingEngine.__calculate_median_plpc(positions, side, rule),
                'stddev_plpc': ChartingEngine.__calculate_stddev_plpc(positions, side, rule)
            }
        return rule_stats

    @staticmethod
    def __calculate_rule_count(positions: List[Position], side: str, rule: str) -> int:
        """Counts the number of positions that were triggered by the given rule."""
        count = 0
        for position in positions:
            if ChartingEngine.__get_rule_from_side(position, side) == rule:
                count += 1
        return count

    @staticmethod
    def __calculate_average_plpc(positions: List[Position], side: str, rule: str) -> float:
        """Calculates the average profit/loss percent of the positions triggers by a given rule."""
        plpc_values = []
        for position in positions:
            if ChartingEngine.__get_rule_from_side(position, side) == rule:
                plpc_values.append(position.lifetime_profit_loss_percent())
        return statistics.mean(plpc_values)

    @staticmethod
    def __calculate_median_plpc(positions: List[Position], side: str, rule: str) -> float:
        """Calculates the median profit/loss percent of the positions triggers by a given rule."""
        plpc_values = []
        for position in positions:
            if ChartingEngine.__get_rule_from_side(position, side) == rule:
                plpc_values.append(position.lifetime_profit_loss_percent())
        return statistics.median(plpc_values)

    @staticmethod
    def __calculate_stddev_plpc(positions: List[Position], side: str, rule: str) -> float:
        """Calculates the stddev (population) profit/loss percent of the positions triggers by a given rule."""
        plpc_values = []
        for position in positions:
            if ChartingEngine.__get_rule_from_side(position, side) == rule:
                plpc_values.append(position.lifetime_profit_loss_percent())
        return statistics.pstdev(plpc_values)

    @staticmethod
    def __get_rule_from_side(position: Position, side: str):
        """Returns the correct rule used to algorithm a position based on side."""
        if side == BUY_SIDE:
            return position.get_buy_rule()
        else:
            return position.get_sell_rule()

    @staticmethod
    def __save_chart(figure_html: str, filename: str) -> str:
        """Saves a chart to a file."""
        chart_filepath = os.path.join('figures', filename)

        # make the directories if they don't already exist
        os.makedirs(os.path.dirname(chart_filepath), exist_ok=True)

        with open(chart_filepath, 'w', encoding="utf-8") as file:
            file.write(figure_html)

        return chart_filepath

    @staticmethod
    def __translate_position_title_from_side(side: str) -> str:
        """Translates the side to a position title."""
        if side == BUY_SIDE:
            return ACQUISITION
        return LIQUIDATION
