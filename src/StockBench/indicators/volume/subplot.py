import numpy as np
from StockBench.indicator.subplot import Subplot
import plotly.graph_objects as fplt
from StockBench.display.display_constants import *


class VolumeSubplot(Subplot):
    """This class is a subclass of the Subplot class.

    A Volume object contains the subplot with volume data.

    Additional traces include:
    """
    def __init__(self):
        super().__init__('volume', [{"type": "bar"}], False)

    @staticmethod
    def get_subplot(df):
        """Builds and returns the subplot.

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
        """builds and returns a list of traces to add to the subplot.

        Args:
            df (DataFrame): The dataframe from the simulation.

        return:
            list: A list of traces to add to the subplot defined in this class.
        """
        return []
