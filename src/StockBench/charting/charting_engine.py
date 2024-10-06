import os
import statistics
import numpy as np
import pandas as pd
from typing import Optional
import plotly.offline as offline
from .display_constants import *
import plotly.graph_objects as plotter
from plotly.subplots import make_subplots
from plotly.figure_factory import create_distplot
from StockBench.function_tools.nonce import datetime_timestamp
from StockBench.constants import *


class ChartingEngine:
    """Base class for a charting engine."""

    TEMP_SAVE = 0
    UNIQUE_SAVE = 1

    PLOTLY_CHART_MARGIN_TOP = 50
    PLOTLY_CHART_MARGIN_BOTTOM = 60
    PLOTLY_CHART_MARGIN_LEFT = 60
    PLOTLY_CHART_MARGIN_RIGHT = 100

    @staticmethod
    def build_rules_bar_chart(positions: list, side: str, symbol: Optional[str], save_option=TEMP_SAVE) -> str:
        """Builds a multi-chart for an analysis of rules of a given side.

        return:
            str: The filepath of the built chart.
        """
        rows = 2
        cols = 1

        side_title = ChartingEngine.__translate_position_title_from_side(side)

        chart_list = [[{"type": "bar"}], [{"type": "bar"}]]
        chart_titles = (f'{side_title} Count per Rule', f'Position Profit/Loss % Analytics per {side_title} Rule')

        # Parent Plot
        fig = make_subplots(rows=rows,
                            cols=cols,
                            shared_xaxes=True,
                            vertical_spacing=0.15,
                            horizontal_spacing=0.05,
                            specs=chart_list,
                            subplot_titles=chart_titles)

        # rule counts chart
        fig.add_trace(ChartingEngine.rule_count_bar(positions, side), 1, 1)

        # rule plpc stats chart (overlayed charts)
        rule_stats_traces = ChartingEngine.rule_stats_traces(positions, side)
        fig.add_trace(rule_stats_traces[0], 2, 1)
        fig.add_trace(rule_stats_traces[1], 2, 1)
        fig.add_trace(rule_stats_traces[2], 2, 1)

        # set the layout
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False)

        # format the chart (remove plotly white border)
        formatted_fig = ChartingEngine.format_chart(fig)

        temp_filename = f'temp_{side}_chart'
        if symbol:
            unique_prefix = f'{symbol}_{side}_rules_bar_chart'
        else:
            unique_prefix = f'multi_{side}_rules_bar_chart'

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, save_option, temp_filename, unique_prefix)

    @staticmethod
    def build_positions_duration_bar_chart(positions: list, symbol: Optional[str], save_option=TEMP_SAVE) -> str:
        """Builds a chart for duration of positions.

        return:
            str: The filepath of the built chart.
        """
        rows = 1
        cols = 1

        chart_list = [[{"type": "bar"}]]
        chart_titles = ('Duration per Position',)

        # Parent Plot
        fig = make_subplots(rows=rows,
                            cols=cols,
                            shared_xaxes=True,
                            vertical_spacing=0.15,
                            horizontal_spacing=0.05,
                            specs=chart_list,
                            subplot_titles=chart_titles)

        # positions analysis traces
        position_analysis_traces = ChartingEngine.positions_duration_bar(positions)

        # position analysis chart (overlayed traces)
        fig.add_trace(position_analysis_traces[0], 1, 1)
        fig.add_trace(position_analysis_traces[1], 1, 1)
        fig.add_trace(position_analysis_traces[2], 1, 1)

        # set the layout
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False)

        # format the chart (remove plotly white border)
        formatted_fig = ChartingEngine.format_chart(fig)

        temp_filename = 'temp_positions_duration_bar_chart'
        if symbol:
            unique_prefix = f'{symbol}_positions_duration_bar_chart'
        else:
            unique_prefix = 'multi_positions_duration_bar_chart'

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, save_option, temp_filename, unique_prefix)

    @staticmethod
    def build_positions_profit_loss_bar_chart(positions: list, symbol: Optional[str], save_option=TEMP_SAVE) -> str:
        """Builds a chart for profit/loss analysis of positions.

        return:
            str: The filepath of the built chart.
        """
        rows = 1
        cols = 1

        chart_list = [[{"type": "bar"}]]
        chart_titles = ('Total Profit/Loss per Position',)

        # Parent Plot
        fig = make_subplots(rows=rows,
                            cols=cols,
                            shared_xaxes=True,
                            vertical_spacing=0.15,
                            horizontal_spacing=0.05,
                            specs=chart_list,
                            subplot_titles=chart_titles)

        # positions analysis traces
        position_analysis_traces = ChartingEngine.positions_total_pl_bar(positions)

        # position analysis chart (overlayed traces)
        fig.add_trace(position_analysis_traces[0], 1, 1)
        fig.add_trace(position_analysis_traces[1], 1, 1)
        fig.add_trace(position_analysis_traces[2], 1, 1)

        # set the layout
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False)

        # format the chart (remove plotly white border)
        formatted_fig = ChartingEngine.format_chart(fig)

        temp_filename = 'temp_positions_profit_loss_bar_chart'
        if symbol:
            unique_prefix = f'{symbol}_positions_profit_loss_bar_chart'
        else:
            unique_prefix = 'multi_positions_profit_loss_bar_chart'

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, save_option, temp_filename, unique_prefix)

    @staticmethod
    def build_positions_profit_loss_histogram_chart(positions: list, strategy_name: str, symbol: Optional[str],
                                                    save_option=TEMP_SAVE) -> str:
        """Build a chart for positions histogram.

        return:
            str: The filepath of the built chart.
        """
        # put the strategy name inside a list so we can use it in the dataset histogram
        strategy_names = [strategy_name]
        positions_data = []

        data_list = []
        for position in positions:
            data_list.append(position.lifetime_profit_loss())
        positions_data.append(data_list)

        formatted_fig = ChartingEngine._build_multi_dataset_histogram(strategy_names, positions_data,
                                                                      'Position Profit/Loss Distribution per Strategy')

        temp_filename = 'temp_positions_profit_loss_histogram_chart'
        if symbol:
            unique_prefix = f'{symbol}_positions_profit_loss_histogram_chart'
        else:
            unique_prefix = 'multi_positions_profit_loss_histogram_chart'

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, save_option, temp_filename, unique_prefix)

    @staticmethod
    def handle_save_chart(formatted_fig, save_option, temp_filename, unique_prefix) -> str:
        """andle save options for charts"""
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
    def format_chart(fig):
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
    def rule_count_bar(positions, side):
        """Build bar chart for the number of trades made for each buy rule."""
        stats = ChartingEngine.__get_rule_statistics(positions, side)

        # extract the data from the stats dict
        rules_list = []
        counts_list = []
        for key in stats.keys():
            rules_list.append(key)
            counts_list.append(stats[key]['count'])

        # create df and add values
        df = pd.DataFrame()
        df['Rule'] = rules_list
        df['Count'] = counts_list

        # build and return trace
        return plotter.Bar(
            x=df['Rule'],
            y=df['Count'],
            marker=dict(color=OFF_BLUE), name='Count')

    @staticmethod
    def rule_stats_traces(positions, side) -> list:
        stats = ChartingEngine.__get_rule_statistics(positions, side)

        # extract the data from the stats dict
        rules_list = []
        avg_list = []
        med_list = []
        stddev_list = []
        for key in stats.keys():
            rules_list.append(key)
            avg_list.append(stats[key]['average_plpc'])
            med_list.append(stats[key]['median_plpc'])
            stddev_list.append(stats[key]['stddev_plpc'])

        # create df and add values
        df = pd.DataFrame()
        df['Rule'] = rules_list
        df['Avg'] = avg_list
        df['Med'] = med_list
        df['Stddev'] = stddev_list

        # build and return traces
        return [plotter.Bar(x=df['Rule'], y=df['Avg'], marker=dict(color=AVG_COLOR), name='Mean'),
                plotter.Bar(x=df['Rule'], y=df['Med'], marker=dict(color=MED_COLOR), name='Median'),
                plotter.Bar(x=df['Rule'], y=df['Stddev'], marker=dict(color=STDDEV_COLOR), name='Stddev')]

    @staticmethod
    def positions_duration_bar(positions):
        durations = []
        for position in positions:
            durations.append(position.duration())

        # create a df to use for total pls (so we can keep track of bar color as well
        df = pd.DataFrame()
        df['duration'] = durations

        # calculate mean and median
        mean = statistics.mean(durations)
        median = statistics.median(durations)

        # assemble the values into a list for plotting
        mean_values = [mean for _ in durations]
        median_values = [median for _ in durations]

        # build and return chart
        return [plotter.Bar(y=df['duration'], name='Duration'),
                plotter.Scatter(y=mean_values, marker=dict(color=MED_COLOR), name='Mean'),
                plotter.Scatter(y=median_values, marker=dict(color=STDDEV_COLOR), name='Median')]

    @staticmethod
    def positions_total_pl_bar(positions):
        total_pls = []
        for position in positions:
            total_pls.append(position.lifetime_profit_loss())

        # create a df to use for total pls (so we can keep track of bar color as well
        df = pd.DataFrame()
        df['total_pl'] = total_pls
        df['color'] = np.where(df['total_pl'] < 0, BEAR_RED, BULL_GREEN)

        # calculate mean and median
        mean = statistics.mean(total_pls)
        median = statistics.median(total_pls)

        # assemble the values into a list for plotting
        mean_values = [mean for _ in total_pls]
        median_values = [median for _ in total_pls]

        # build and return chart
        return [plotter.Bar(y=df['total_pl'], marker_color=df['color'], name='Profit/Loss'),
                plotter.Scatter(y=mean_values, marker=dict(color=MED_COLOR), name='Mean'),
                plotter.Scatter(y=median_values, marker=dict(color=STDDEV_COLOR), name='Median')]

    @staticmethod
    def _build_multi_dataset_histogram(strategy_names: list, positions_data: list, title: str):
        """Build a multi-dataset histogram chart."""
        fig = create_distplot(positions_data, strategy_names)

        # set the layout
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, title=title)

        # format the chart (remove plotly white border)
        return ChartingEngine.format_chart(fig)

    @staticmethod
    def __get_rule_statistics(positions, side) -> dict:
        """Builds a dict of statistics for each rule based for the given side."""
        rule_stats = {}
        for position in positions:
            rule = ChartingEngine.__get_rule_from_side(position, side)

            # create a new key : value for the rule
            rule_stats[rule] = {}

            # FIXME: these calls may need to be multi-processed so it is not as slow for longer simulations
            # add statistics to the rule here
            rule_stats[rule]['count'] = ChartingEngine.__calculate_rule_count(positions, side, rule)
            rule_stats[rule]['average_plpc'] = ChartingEngine.__calculate_average_plpc(positions, side, rule)
            rule_stats[rule]['median_plpc'] = ChartingEngine.__calculate_median_plpc(positions, side, rule)
            rule_stats[rule]['stddev_plpc'] = ChartingEngine.__calculate_stddev_plpc(positions, side, rule)
        return rule_stats

    @staticmethod
    def __calculate_rule_count(positions, side, rule) -> int:
        """Counts the number of positions that were triggered by the given rule."""
        count = 0
        for position in positions:
            if ChartingEngine.__get_rule_from_side(position, side) == rule:
                count += 1
        return count

    @staticmethod
    def __calculate_average_plpc(positions, side, rule) -> float:
        """Calculates the average profit/loss percent of the positions triggers by a given rule."""
        plpc_values = []
        for position in positions:
            if ChartingEngine.__get_rule_from_side(position, side) == rule:
                plpc_values.append(position.lifetime_profit_loss_percent())
        return statistics.mean(plpc_values)

    @staticmethod
    def __calculate_median_plpc(positions, side, rule) -> float:
        """Calculates the median profit/loss percent of the positions triggers by a given rule."""
        plpc_values = []
        for position in positions:
            if ChartingEngine.__get_rule_from_side(position, side) == rule:
                plpc_values.append(position.lifetime_profit_loss_percent())
        return statistics.median(plpc_values)

    @staticmethod
    def __calculate_stddev_plpc(positions, side, rule) -> float:
        """Calculates the stddev (population) profit/loss percent of the positions triggers by a given rule."""
        plpc_values = []
        for position in positions:
            if ChartingEngine.__get_rule_from_side(position, side) == rule:
                plpc_values.append(position.lifetime_profit_loss_percent())
        return statistics.pstdev(plpc_values)

    @staticmethod
    def __get_rule_from_side(position, side):
        """Returns the correct rule used to algorithm a position based on side."""
        if side == 'buy':
            return position.get_buy_rule()
        else:
            return position.get_sell_rule()

    @staticmethod
    def __save_chart(figure, filename) -> str:
        """Saves a chart to a file.

        Args:
            figure(str): The html string of the chart.
            filename(str): The name of the file to save as.

        Return:
            (str): The filepath of the saved chart.
        """
        chart_filepath = os.path.join('figures', filename)
        # make the directories if they don't already exist
        os.makedirs(os.path.dirname(chart_filepath), exist_ok=True)

        with open(chart_filepath, 'w', encoding="utf-8") as file:
            file.write(figure)

        return chart_filepath

    @staticmethod
    def __translate_position_title_from_side(side: str) -> str:
        """Translates the side to a position title.

        return:
            str: The translated position title.
        """
        if side == BUY_SIDE:
            return ACQUISITION
        return LIQUIDATION
