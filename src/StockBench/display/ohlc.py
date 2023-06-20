import re
from .subplot import Subplot
import plotly.graph_objects as fplt
from StockBench.display.display_constants import *


class OHLC(Subplot):
    """This class is a subclass of the Subplot class.

    A OHLC object contains the subplot with candlestick price data.

    Additional traces include:
        - SMA curves
        - Buy points
        - Sell points
    """
    def __init__(self):
        super().__init__('OHLC', [{"type": "ohlc"}])

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
        for (column_name, column_data) in df.items():
            if 'SMA' in column_name:
                nums = re.findall(r'\d+', column_name)
                length = nums[0]
                traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=df[column_name],
                    line=dict(color=SMA_COLOR, width=MOVING_AVERAGE_LINE_WIDTH),
                    name=f'SMA{length}'))
            if 'EMA' in column_name:
                nums = re.findall(r'\d+', column_name)
                length = nums[0]
                traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=df[column_name],
                    line=dict(color=EMA_COLOR, width=MOVING_AVERAGE_LINE_WIDTH),
                    name=f'EMA{length}'))
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



