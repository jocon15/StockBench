from .subplot import Subplot
import plotly.graph_objects as fplt


class Volume(Subplot):
    def __init__(self):
        super().__init__([{"type": "bar"}])

    @staticmethod
    def get_subplot(df):
        """Builds and returns the subplot.

        Args:
            df (DataFrame): The dataframe from the simulation.

        return:
            A plotly subplot.
        """
        return fplt.Bar(
                    x=df['Date'],
                    y=df['volume'])

    @staticmethod
    def get_traces(df) -> list:
        """builds and returns a list of traces to add to the subplot.

        Args:
            df (DataFrame): The dataframe from the simulation.

        return:
            list: A list of traces to add to the subplot defined in this class.
        """
        return []
