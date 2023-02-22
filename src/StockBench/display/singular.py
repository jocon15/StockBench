import os
import logging
from .rsi import RSI
from .ohlc import OHLC
from .volume import Volume
from .display_constants import *
from plotly.subplots import make_subplots
from StockBench.function_tools.nonce import datetime_nonce

log = logging.getLogger()


class SingularDisplay:
    """This class defines a display object.

    The display object is used as an API for the simulator to chart the data. All display functionality is done
    through this API.
    """
    def __init__(self):
        self.__df = None

        self.__subplot_objects = list()
        self.__subplot_types = list()

    def chart(self, df, symbol, show=True, save=False):
        """Chart the data.

        Args:
            df (DataFrame): The full DataFrame post-simulation.
            symbol (str): The symbol the simulation was run on.
            show (bool): Show the chart.
            save (bool): Save the chart.
        """
        self.__df = df

        # add the ohlc because that's always there
        self.__subplot_objects.append(OHLC())

        # activate the subplot objects if evidence is found in the df
        for (column_name, column_data) in self.__df.iteritems():
            if column_name == 'RSI':
                self.__subplot_objects.append(RSI())
            if column_name == 'volume':
                self.__subplot_objects.append(Volume())

        # get the subplot types
        for subplot in self.__subplot_objects:
            self.__subplot_types.append(subplot.get_type())

        # build the parent plot
        cols = col = 1  # only one col in every row
        rows = len(self.__subplot_objects)
        fig = make_subplots(rows=rows, cols=cols, shared_xaxes=True, vertical_spacing=0.06, specs=self.__subplot_types)

        # add subplots and traces from the objects to the parent plot
        for enum_row, subplot in enumerate(self.__subplot_objects):
            row = enum_row + 1
            fig.add_trace(subplot.get_subplot(self.__df), row=row, col=col)
            for trace in subplot.get_traces(self.__df):
                fig.add_trace(trace, row=row, col=col)

        # if we need to add any color changes, do it here

        # update the layout
        window_size = len(self.__df['Close'])
        fig.update_layout(template='plotly_dark', title=f'{window_size} day simulation for {symbol}',
                          xaxis_title='Date', yaxis_title='Price (USD)', xaxis_rangeslider_visible=False)

        chart_filepath = os.path.join('figures', f'figure_{symbol}_{datetime_nonce()}.html')
        # make the directories if they don't already exist
        os.makedirs(os.path.dirname(chart_filepath), exist_ok=True)

        if show and not save:
            fig.show()
        if save and not show:
            fig.write_html(chart_filepath, auto_open=False)
        if show and save:
            fig.write_html(chart_filepath, auto_open=True)
