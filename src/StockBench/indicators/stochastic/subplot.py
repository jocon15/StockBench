import plotly.graph_objects as fplt
from pandas import DataFrame

from StockBench.indicator.subplot import Subplot
from StockBench.charting.display_constants import WHITE, HORIZONTAL_TRIGGER_YELLOW


class StochasticSubplot(Subplot):
    """This class is a subclass of the Subplot class.

    A Stochastic object contains the subplot with stochastic oscillator data.

    Additional traces include:
        - RSI upper algorithm
        - RSI lower algorithm
    """
    def __init__(self):
        super().__init__('stochastic', [{"type": "scatter"}], False)

    def get_subplot(self, df: DataFrame):
        """Builds and returns the subplot.

        Args:
            df: The dataframe of simulation data.

        return:
            A plotly subplot.
        """
        return fplt.Scatter(
            x=df['Date'],
            y=df[self.data_symbol],
            line=dict(color=WHITE),
            name='Stochastic')

    def get_traces(self, df: DataFrame) -> list:
        """builds and returns a list of traces to add to the subplot.

        Args:
            df: The dataframe of simulation data.

        return:
            list: A list of traces to add to the subplot defined in this class.
        """
        # builds and returns a list of traces to add to the subplot
        traces = []
        for (column_name, column_data) in df.items():
            if column_name == 'stochastic_upper':
                traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=df['stochastic_upper'],
                    line=dict(color=HORIZONTAL_TRIGGER_YELLOW),
                    name='Stochastic Upper'))
            if column_name == 'stochastic_lower':
                traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=df['stochastic_lower'],
                    line=dict(color=HORIZONTAL_TRIGGER_YELLOW),
                    name='Stochastic Lower'))

        return traces
