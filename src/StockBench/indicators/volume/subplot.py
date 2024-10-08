import numpy as np
from StockBench.indicator.subplot import Subplot
import plotly.graph_objects as fplt
from StockBench.charting.display_constants import BEAR_RED, BULL_GREEN


class VolumeSubplot(Subplot):
    """Subplot for the volume indicator.

    Additional traces include:
    """
    def __init__(self):
        super().__init__('volume', [{"type": "bar"}], False)

    @staticmethod
    def get_subplot(df):
        """Builds the subplot.

        Args:
            df (DataFrame): The dataframe from the simulation.

        return:
            A plotly subplot.
        """
        df['volume_colors'] = np.where(df['color'] == 'red', BEAR_RED, BULL_GREEN)
        return fplt.Bar(
                    x=df['Date'],
                    y=df['volume'],
                    name='Volume',
                    marker_color=df['volume_colors'])

    @staticmethod
    def get_traces(df) -> list:
        """Build a list of traces to add to the subplot.

        Args:
            df (DataFrame): The dataframe from the simulation.

        return:
            list: A list of traces to add to the subplot defined in this class.
        """
        return []
