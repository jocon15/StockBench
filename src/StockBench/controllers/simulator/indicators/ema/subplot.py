import re
import plotly.graph_objects as fplt
from pandas import DataFrame

from StockBench.controllers.simulator.indicator.subplot import Subplot
from StockBench.controllers.charting.display_constants import EMA_COLOR, MOVING_AVERAGE_LINE_WIDTH


class EMASubplot(Subplot):
    def __init__(self):
        super().__init__('EMA', [{}], is_ohlc_trace=True)

    def get_subplot(self, df: DataFrame):
        # Dummy subplot - provides an implementation but should never be used
        # only the get_traces function should be used
        return None

    def get_traces(self, df: DataFrame):
        # sma is only an OHLC trace
        traces = []
        for (column_name, column_data) in df.items():
            if self.data_symbol in column_name:
                nums = re.findall(r'\d+(?:\.\d+)?', column_name)
                length = nums[0]
                traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=df[column_name],
                    line=dict(color=EMA_COLOR, width=MOVING_AVERAGE_LINE_WIDTH),
                    name=f'{self.data_symbol}{length}'))
        return traces
