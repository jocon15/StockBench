import plotly.graph_objects as fplt
from plotly.graph_objects import Ohlc, Scatter
from pandas import DataFrame
from typing import List

from StockBench.controllers.simulator.indicator.subplot import Subplot
from StockBench.controllers.charting.display_constants import BUY_COLOR, SELL_COLOR, BUY_SELL_DOTS_WIDTH


class OHLCSubplot(Subplot):
    """Subplot of the stock price in candlestick format."""
    DATE_COLUMN = 'Date'
    BUY_COLUMN = 'Buy'
    SELL_COLUMN = 'Sell'
    OPEN_COLUMN = 'Open'
    HIGH_COLUMN = 'High'
    LOW_COLUMN = 'Low'
    CLOSE_COLUMN = 'Close'  
    
    def __init__(self):
        super().__init__('OHLC', [{"type": "ohlc"}], False)

    def get_subplot(self, df: DataFrame) -> Ohlc:
        """Builds a subplot.

        Args:
            df (DataFrame): The dataframe from the simulation.

        return:
            Ohlc: A plotly OHLC subplot.
        """
        return fplt.Ohlc(x=df[self.DATE_COLUMN],
                         open=df[self.OPEN_COLUMN],
                         high=df[self.HIGH_COLUMN],
                         low=df[self.LOW_COLUMN],
                         close=df[self.CLOSE_COLUMN],
                         name='Price Data')

    def get_traces(self, df: DataFrame) -> List[Scatter]:
        """Builds a list of traces to add to the subplot.

        Args:
            df (DataFrame): The simulation data.

        return:
            list: A list of scatter traces to add to the OHLC subplot.
        """
        traces = []
        for (column_name, column_data) in df.items():
            if column_name == self.BUY_COLUMN:
                traces.append(fplt.Scatter(
                    x=df[self.DATE_COLUMN],
                    y=df[self.BUY_COLUMN],
                    name=self.BUY_COLUMN,
                    mode='markers',
                    marker=dict(color=BUY_COLOR, size=BUY_SELL_DOTS_WIDTH)))
            if column_name == self.SELL_COLUMN:
                traces.append(fplt.Scatter(
                    x=df[self.DATE_COLUMN],
                    y=df[self.SELL_COLUMN],
                    name=self.SELL_COLUMN,
                    mode='markers',
                    marker=dict(color=SELL_COLOR, size=BUY_SELL_DOTS_WIDTH)))

        return traces
