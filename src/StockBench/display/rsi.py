from .subplot import Subplot
import plotly.graph_objects as fplt
from StockBench.display.display_constants import *


class RSI(Subplot):
    def __init__(self):
        super().__init__([{"type": "scatter"}])

    @staticmethod
    def get_subplot(df):
        """Builds and returns the subplot.

        Args:
            df (DataFrame): The dataframe from the simulation.

        return:
            A plotly subplot.
        """
        return fplt.Scatter(
                    x=df['Date'],
                    y=df['RSI'],
                    line=dict(color=WHITE),
                    name='RSI')

    @staticmethod
    def get_traces(df) -> list:
        """builds and returns a list of traces to add to the subplot.

        Args:
            df (DataFrame): The dataframe from the simulation.

        return:
            list: A list of traces to add to the subplot defined in this class.
        """
        # builds and returns a list of traces to add to the subplot
        traces = list()
        for (column_name, column_data) in df.iteritems():
            if column_name == 'RSI_upper':
                traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=df['RSI_upper'],
                    line=dict(color=HORIZONTAL_TRIGGER_YELLOW),
                    name='RSI Upper'))
            if column_name == 'RSI_lower':
                traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=df['RSI_lower'],
                    line=dict(color=HORIZONTAL_TRIGGER_YELLOW),
                    name='RSI Lower'))
                
        return traces
