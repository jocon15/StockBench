import os
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

    def handle_save_chart(self, formatted_fig, show, save_option, temp_filename, unique_prefix) -> str:
        """andle save options for charts"""
        if save_option == Display.TEMP_SAVE:
            # save chart as temporary file - will be overwritten by any new chart
            chart_filepath = self.save_chart(formatted_fig, f'{temp_filename}.html')
        elif save_option == Display.UNIQUE_SAVE:
            # save chart as unique file for persistent saving
            chart_filepath = self.save_chart(formatted_fig, f'{unique_prefix}_{datetime_timestamp()}.html')
        else:
            # no chart was saved
            chart_filepath = ''

        if show:
            formatted_fig.show()

        return chart_filepath

    @staticmethod
    def save_chart(figure, filename) -> str:
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
    def buy_rule_count_bar(positions):
        """Bar chart for the number of trades made for each buy rule"""
        rules_list, counts_list = Display.__get_rules_count_lists(positions, 'buy')

        # create df and add values
        df = pd.DataFrame()
        df['Rule'] = rules_list
        df['Count'] = counts_list

        # build and return chart
        return plotter.Bar(
            x=df['Rule'],
            y=df['Count'],
            marker=dict(color=OFF_BLUE))

    @staticmethod
    def sell_rule_count_bar(positions):
        """Bar chart for the number of trades made for each buy rule."""
        rules_list, counts_list = Display.__get_rules_count_lists(positions, 'sell')

        # create df and add values
        df = pd.DataFrame()
        df['Rule'] = rules_list
        df['Count'] = counts_list

        # build and return chart
        return plotter.Bar(
            x=df['Rule'],
            y=df['Count'],
            marker=dict(color=OFF_BLUE))

    @staticmethod
    def __get_rules_count_lists(positions, side) -> tuple:
        """Counts the number of positions that were triggered by each rule

        return:
            tuple: (rules list, counts list)

        example return:
            (['SMA20>0', 'RSI>30'], [12, 35])
        """
        rule_counts = []  # list of tuples
        for position in positions:
            match_found = False
            if side == 'buy':
                rule = position.get_buy_rule()
            else:
                rule = position.get_sell_rule()
            for element in rule_counts:
                if rule == element[0]:
                    match_found = True
                    element[1] = element[1] + 1
                    break
            if not match_found:
                # create new rule count tuple
                rule_counts.append([rule, 1])

        # convert the list into respective lists for the df
        rules_list = [x[0] for x in rule_counts]
        counts_list = [x[1] for x in rule_counts]

        return rules_list, counts_list
