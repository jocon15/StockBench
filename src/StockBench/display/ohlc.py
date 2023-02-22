import re
from .subplot import Subplot
import plotly.graph_objects as fplt
from StockBench.display.display_constants import *

'''Reminder that if ohlc and rsi share any attributes, we can make a subplot superclass to keep it DRY

Type is a shared attribute, and get_type() is a shared method, so you instantiate the superclass and pass 
it the [{}] value for the type 
'''


class OHLC(Subplot):
    def __init__(self):
        super().__init__([{"type": "ohlc"}])

    @staticmethod
    def get_subplot(df):
        """Builds and returns the subplot.

        Args:
            df (DataFrame): The dataframe from the simulation.

        return:
            A plotly subplot.
        """
        return fplt.Ohlc(x=df['Date'],
                         open=df['Open'],
                         high=df['High'],
                         low=df['Low'],
                         close=df['Close'],
                         name='Price Data')

    @staticmethod
    def get_traces(df) -> list:
        """builds and returns a list of traces to add to the subplot.

        Args:
            df (DataFrame): The dataframe from the simulation.

        return:
            list: A list of traces to add to the subplot defined in this class.
        """
        traces = list()
        for (column_name, column_data) in df.iteritems():
            if 'SMA' in column_name:
                nums = re.findall(r'\d+', column_name)
                length = nums[0]
                traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=df[column_name], line=dict(color=WHITE),
                    name=f'SMA{length}'))
            if column_name == 'Buy':
                traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=df['Buy'],
                    name='Buy',
                    mode='markers',
                    marker=dict(color=BUY_COLOR)))
            if column_name == 'Sell':
                traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=df['Sell'],
                    name='Sell',
                    mode='markers',
                    marker=dict(color=SELL_COLOR)))

        return traces



