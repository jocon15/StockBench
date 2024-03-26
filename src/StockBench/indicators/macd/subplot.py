import plotly.graph_objects as fplt
from StockBench.indicator.subplot import Subplot


class MACDSubplot(Subplot):
    """"""
    def __init__(self):
        super().__init__('MACD', [{"type": "bar"}], False)

    @staticmethod
    def get_subplot(df):
        """"""
        return fplt.Bar(x=df['Date'], y=df['MACD'], name='MACD')

    @staticmethod
    def get_traces(self) -> list:
        """"""
        return []
