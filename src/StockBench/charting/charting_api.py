import re
import logging
import pandas as pd
from .color_constants import *
import plotly.graph_objects as fplt
from plotly.subplots import make_subplots

log = logging.getLogger()


class ChartingAPI:
    """This class defines a charting object.

    The charting object is used as an API for the simulator to chart the data. All charting functionality is done
    through this API.
    """
    def __init__(self):
        self.__subplot_count = 1
        self.__df = None

        self.__next_row = 2
        # add any more constants here...
        self.__rsi_row = None

    def chart(self, _df, _symbol):
        # FIXME: Might need to take in a filepath to output the html file to
        """Chart the data.

        Args:
            _df (DataFrame): The full DataFrame post-simulation.
            _symbol (str): The symbol the simulation was run on.
        """
        self.__df = _df

        rows = 1
        cols = 1
        chart_list = [[{"type": "ohlc"}]]
        # get the subplot count
        for (column_name, column_data) in self.__df.iteritems():
            if column_name == 'RSI':
                chart_list.append([{"type": "scatter"}])
                rows += 1
            if column_name == 'volume':
                chart_list.append([{"type": "bar"}])
                rows += 1
            # here you would add any other checks for additional subplots (rows/cols)

        # create the parent plot
        fig = make_subplots(rows=rows, cols=cols, shared_xaxes=True, vertical_spacing=0.06, specs=chart_list)

        # add default OHLC trace
        fig.add_trace(fplt.Ohlc(x=self.__df['Date'],
                                open=self.__df['Open'],
                                high=self.__df['High'],
                                low=self.__df['Low'],
                                close=self.__df['Close'],
                                name='Price Data'), row=1, col=1)

        # add additional traces
        for (column_name, column_data) in self.__df.iteritems():
            if 'SMA' in column_name:
                nums = re.findall(r'\d+', column_name)
                length = nums[0]
                fig.add_trace(fplt.Scatter(
                    x=self.__df['Date'],
                    y=self.__df[column_name], line=dict(color=WHITE),
                    name=f'SMA{length}'),
                    row=1, col=1)
            if column_name == 'Buy':
                fig.add_trace(fplt.Scatter(
                    x=self.__df['Date'],
                    y=self.__df['Buy'],
                    name='Buy',
                    mode='markers',
                    marker=dict(color=BUY_COLOR)),
                    row=1, col=1)
            if column_name == 'Sell':
                fig.add_trace(fplt.Scatter(
                    x=self.__df['Date'],
                    y=self.__df['Sell'],
                    name='Sell',
                    mode='markers',
                    marker=dict(color=SELL_COLOR)),
                    row=1, col=1)
            if column_name == 'RSI':
                fig.add_trace(fplt.Scatter(
                    x=self.__df['Date'],
                    y=self.__df['RSI'],
                    line=dict(color=WHITE),
                    name='RSI'),
                    row=self.__next_row, col=1)
                self.__rsi_row = self.__next_row
                self.__next_row += 1
            if column_name == 'RSI_upper':
                fig.add_trace(fplt.Scatter(
                    x=self.__df['Date'],
                    y=self.__df['RSI_upper'],
                    line=dict(color=HORIZONTAL_TRIGGER_YELLOW),
                    name='RSI Upper'),
                    row=self.__rsi_row, col=1)
            if column_name == 'RSI_lower':
                fig.add_trace(fplt.Scatter(
                    x=self.__df['Date'],
                    y=self.__df['RSI_lower'],
                    line=dict(color=HORIZONTAL_TRIGGER_YELLOW),
                    name='RSI Lower'),
                    row=self.__rsi_row, col=1)
            if column_name == 'volume':
                fig.add_trace(fplt.Bar(
                    x=self.__df['Date'],
                    y=self.__df['volume']),
                    row=self.__next_row,
                    col=1)
                fig.update_traces(marker_color=BULL_GREEN, selector=dict(type='bar'))
                fig.update_traces(name='volume', selector=dict(type='bar'))
                self.__next_row += 1

        # update the layout
        window_size = len(self.__df['Close'])
        fig.update_layout(template='plotly_dark', title=f'{window_size} day simulation for {_symbol}',
                          xaxis_title='Date', yaxis_title='Price (USD)', xaxis_rangeslider_visible=False)

        fig.write_html('figure.html', auto_open=True)
