import os
import statistics
import pandas as pd
import plotly.offline as offline
from .display_constants import *
import plotly.graph_objects as plotter
from StockBench.function_tools.nonce import datetime_timestamp


class Display:
    """Base class for a display."""

    NO_SAVE = 0
    TEMP_SAVE = 1
    UNIQUE_SAVE = 2

    def handle_save_chart(self, formatted_fig, save_option, temp_filename, unique_prefix) -> str:
        """andle save options for charts"""
        if save_option == Display.TEMP_SAVE:
            # save chart as temporary file - will be overwritten by any new chart
            chart_filepath = self.__save_chart(formatted_fig, f'{temp_filename}.html')
        elif save_option == Display.UNIQUE_SAVE:
            # save chart as unique file for persistent saving
            chart_filepath = self.__save_chart(formatted_fig, f'{unique_prefix}_{datetime_timestamp()}.html')
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
                                        <body style="background-color:#202124;">
                                        </head>
                                        <body>
                                        {plot_div:s}
                                        </body>""".format(plot_div=plot_div)

        return formatted_fig

    @staticmethod
    def rule_count_bar(positions, side):
        """Build bar chart for the number of trades made for each buy rule."""
        stats = Display.__get_rule_statistics(positions, side)

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
            marker=dict(color=OFF_BLUE))

    @staticmethod
    def rule_stats_traces(positions, side) -> list:
        stats = Display.__get_rule_statistics(positions, side)

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
        return [plotter.Bar(x=df['Rule'], y=df['Avg'], marker=dict(color=AVG_COLOR)),
                plotter.Bar(x=df['Rule'], y=df['Med'], marker=dict(color=MED_COLOR)),
                plotter.Bar(x=df['Rule'], y=df['Stddev'], marker=dict(color=STDDEV_COLOR))]

    @staticmethod
    def positions_total_pl_bar(positions):
        total_pls = []
        for position in positions:
            total_pls.append(position.lifetime_profit_loss())

        # calculate mean and median
        mean = statistics.mean(total_pls)
        median = statistics.median(total_pls)

        # assemble the values into a list for plotting
        mean_values = [mean for _ in total_pls]
        median_values = [median for _ in total_pls]

        # build and return chart
        return [plotter.Bar(y=total_pls, marker=dict(color=AVG_COLOR)),
                plotter.Scatter(y=mean_values, marker=dict(color=WHITE)),
                plotter.Scatter(y=median_values, marker=dict(color=WHITE))]

    @staticmethod
    def __get_rule_statistics(positions, side) -> dict:
        """Builds a dict of statistics for each rule based for the given side."""
        rule_stats = {}
        for position in positions:
            rule = Display.__get_rule_from_side(position, side)

            # create a new key : value for the rule
            rule_stats[rule] = {}

            # FIXME: these calls may need to be multi-processed so it is not as slow for longer simulations
            # add statistics to the rule here
            rule_stats[rule]['count'] = Display.__calculate_rule_count(positions, side, rule)
            rule_stats[rule]['average_plpc'] = Display.__calculate_average_plpc(positions, side, rule)
            rule_stats[rule]['median_plpc'] = Display.__calculate_median_plpc(positions, side, rule)
            rule_stats[rule]['stddev_plpc'] = Display.__calculate_stddev_plpc(positions, side, rule)
        return rule_stats

    @staticmethod
    def __calculate_rule_count(positions, side, rule) -> int:
        """Counts the number of positions that were triggered by the given rule."""
        count = 0
        for position in positions:
            if Display.__get_rule_from_side(position, side) == rule:
                count += 1
        return count

    @staticmethod
    def __calculate_average_plpc(positions, side, rule) -> float:
        """Calculates the average profit/loss percent of the positions triggers by a given rule."""
        plpc_values = []
        for position in positions:
            if Display.__get_rule_from_side(position, side) == rule:
                plpc_values.append(position.lifetime_profit_loss_percent())
        return statistics.mean(plpc_values)

    @staticmethod
    def __calculate_median_plpc(positions, side, rule) -> float:
        """Calculates the median profit/loss percent of the positions triggers by a given rule."""
        plpc_values = []
        for position in positions:
            if Display.__get_rule_from_side(position, side) == rule:
                plpc_values.append(position.lifetime_profit_loss_percent())
        return statistics.median(plpc_values)

    @staticmethod
    def __calculate_stddev_plpc(positions, side, rule) -> float:
        """Calculates the stddev (population) profit/loss percent of the positions triggers by a given rule."""
        plpc_values = []
        for position in positions:
            if Display.__get_rule_from_side(position, side) == rule:
                plpc_values.append(position.lifetime_profit_loss_percent())
        return statistics.pstdev(plpc_values)

    @staticmethod
    def __get_rule_from_side(position, side):
        """Returns the correct rule used to trigger a position based on side."""
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
