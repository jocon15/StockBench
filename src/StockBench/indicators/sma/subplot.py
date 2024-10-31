import re
import plotly.graph_objects as fplt
from pandas import DataFrame

from StockBench.indicator.subplot import Subplot
from StockBench.charting.display_constants import SMA_COLOR, MOVING_AVERAGE_LINE_WIDTH


class SMASubplot(Subplot):
    def __init__(self):
        # but make sure that the subplot is defined as an OHLC trace
        super().__init__('SMA', [{}], is_ohlc_trace=True)

    def get_subplot(self, df: DataFrame):
        # Dummy subplot - provides an implementation but should never be used
        # only the get_traces function should be used
        return None

    def get_traces(self, df: DataFrame):
        # sma is only an OHLC trace
        traces = []
        for (column_name, column_data) in df.items():
            if self.data_symbol in column_name:
                nums = re.findall(r'\d+', column_name)
                length = nums[0]
                traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=df[column_name],
                    line=dict(color=SMA_COLOR, width=MOVING_AVERAGE_LINE_WIDTH),
                    name=f'{self.data_symbol}{length}'))
        return traces
