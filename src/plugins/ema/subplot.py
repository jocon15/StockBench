import re
import plotly.graph_objects as fplt
from StockBench.display.subplot import Subplot
from StockBench.display.display_constants import *


class DummySubplot(Subplot):
    def __init__(self):
        # Dummy subplot so filling out any info in not necessary
        # but make sure that the subplot is defined as an OHLC trace
        super().__init__('', [{}], is_ohlc_trace=True)

    @staticmethod
    def get_subplot(df):
        # Dummy subplot - provides an implementation but should never be used
        # only the get_traces function should be used
        return None

    @staticmethod
    def get_traces(df):
        # sma is only an OHLC trace
        traces = []
        for (column_name, column_data) in df.items():
            if 'EMA' in column_name:
                nums = re.findall(r'\d+', column_name)
                length = nums[0]
                traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=df[column_name],
                    line=dict(color=EMA_COLOR, width=MOVING_AVERAGE_LINE_WIDTH),
                    name=f'EMA{length}'))
        return traces
