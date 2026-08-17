import plotly.graph_objects as fplt
from pandas import DataFrame
from plotly.graph_objs import Scatter

from StockBench.controllers.simulator.indicator.subplot_interface import SubplotInterface
from StockBench.controllers.charting.display_constants import HORIZONTAL_TRIGGER_YELLOW
from StockBench.controllers.simulator.indicator.exceptions import SimulationDataException


class StochasticSubplot(SubplotInterface):
    """This class is a subclass of the Subplot class.

    A Stochastic object contains the subplot with main stochastic oscillator data. If multiple lengths of the indicator
    are used, they will be added as traces.

    Additional traces include:
        - RSI upper algorithm
        - RSI lower algorithm
    """

    def __init__(self):
        super().__init__('stochastic', [{"type": "scatter"}], False)

    def get_subplot(self, df: DataFrame) -> Scatter:
        """Builds the subplot.

        This subplot could contain any number custom length (primary) stochastic oscillator traces.
        EX: 20stochastic, 30stochastic, stochastic, etc.

        They will all end up on the same subplot because they share the same scale.
        """
        primary_traces = []
        primary_trace_names = []
        for (column_name, column_data) in df.items():
            if {self.data_symbol} in column_name and column_name not in primary_trace_names:
                primary_traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=column_data,
                    # line=dict(color=WHITE),  # we want the color to change between
                    name=column_name))

        if not primary_traces:
            raise SimulationDataException('Stochastic subplot build invoked but no data element labeled stochastic was '
                                          'encountered!')

        subplot = primary_traces[0]
        for trace in primary_traces:
            subplot.add_trace(trace)

        return subplot

    def get_traces(self, df: DataFrame) -> list:
        """Builds and a list of traces to add to the subplot."""
        # builds and returns a list of traces to add to the subplot
        traces = []
        for (column_name, column_data) in df.items():
            # stochastic + underscore indicates it is a stochastic trigger value
            if f'{self.data_symbol}_' in column_name:
                traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=df[column_name],
                    line=dict(color=HORIZONTAL_TRIGGER_YELLOW),
                    name=column_name))

        return traces
