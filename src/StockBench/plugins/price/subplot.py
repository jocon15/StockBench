import plotly.graph_objects as fplt
from StockBench.display.subplot import Subplot
from StockBench.display.display_constants import *


class OHLCSubplot(Subplot):
    """This class is a subclass of the Subplot class.

    A OHLC object contains the subplot with candlestick price data.

    Additional traces include:
        - SMA curves
        - Buy points
        - Sell points
    """
    def __init__(self):
        super().__init__('OHLC', [{"type": "ohlc"}], False)

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
        traces = []
        for (column_name, column_data) in df.items():
            if column_name == 'Buy':
                traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=df['Buy'],
                    name='Buy',
                    mode='markers',
                    marker=dict(color=BUY_COLOR, size=BUY_SELL_DOTS_WIDTH)))
            if column_name == 'Sell':
                traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=df['Sell'],
                    name='Sell',
                    mode='markers',
                    marker=dict(color=SELL_COLOR, size=BUY_SELL_DOTS_WIDTH)))

        return traces
