import plotly.graph_objects as fplt
from StockBench.controllers.indicator import Subplot


class MACDSubplot(Subplot):
    """Subplot for the MACD indicator.

    Additional traces include:
    """
    def __init__(self):
        super().__init__('MACD', [{"type": "bar"}], False)

    def get_subplot(self, df):
        """Builds the subplot.

        Args:
            df (DataFrame): The dataframe from the simulation.

        return:
            A plotly subplot.
        """
        return fplt.Bar(x=df['Date'], y=df[self.data_symbol], name=self.data_symbol)

    def get_traces(self, df) -> list:
        """Build a list of traces to add to the subplot.

        Args:
            df (DataFrame): The dataframe from the simulation.

        return:
            list: A list of traces to add to the subplot defined in this class.
        """
        return []
