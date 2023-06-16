from .subplot import Subplot
import plotly.graph_objects as fplt
from .display_constants import *


class Stochastic(Subplot):
    """This class is a subclass of the Subplot class.

    A Stochastic object contains the subplot with stochastic oscillator data.

    Additional traces include:
        - RSI upper trigger
        - RSI lower trigger
    """
    def __init__(self):
        super().__init__('stochastic', [{"type": "scatter"}])

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
            y=df['stochastic_oscillator'],
            line=dict(color=WHITE),
            name='Stochastic')

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
        for (column_name, column_data) in df.items():
            if column_name == 'RSI_upper':
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
