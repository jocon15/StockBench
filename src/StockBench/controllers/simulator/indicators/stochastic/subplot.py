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

    Primary subplot traces include:
        - Default length stochastic (14)
        - Custom length stochastic

    Additional traces include:
        - RSI upper algorithm
        - RSI lower algorithm
    """

    def __init__(self):
        super().__init__('stochastic', [{"type": "scatter"}], False)

        self.remaining_traces = []

    def get_subplot(self, df: DataFrame) -> Scatter:
        """Builds the subplot.

        Note: All primary subplot traces end up on the same subplot because they share the same scale.
        """
        primary_traces = []
        primary_trace_names = []
        for (column_name, column_data) in df.items():
            if self.data_symbol in column_name and column_name not in primary_trace_names:
                primary_traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=column_data,
                    # line=dict(color=WHITE),  # we want the color to change between traces
                    name=column_name))

        if not primary_traces:
            raise SimulationDataException('Stochastic subplot build invoked but no data element labeled stochastic was '
                                          'encountered!')

        # store remaining traces
        self.remaining_traces = primary_traces.copy()
        self.remaining_traces.pop(0)

        return primary_traces[0]

    def get_traces(self, df: DataFrame) -> list:
        """Builds and a list of traces to add to the subplot."""
        # builds and returns a list of traces to add to the subplot
        for (column_name, column_data) in df.items():
            # stochastic + underscore indicates it is a stochastic trigger value
            if f'{self.data_symbol}_' in column_name:
                self.remaining_traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=df[column_name],
                    line=dict(color=HORIZONTAL_TRIGGER_YELLOW),
                    name=column_name))

        return self.remaining_traces
