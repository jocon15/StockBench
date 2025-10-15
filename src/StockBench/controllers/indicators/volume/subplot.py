import numpy as np
import plotly.graph_objects as fplt
from pandas import DataFrame

from StockBench.controllers.indicator import Subplot
from StockBench.controllers.charting import BEAR_RED, BULL_GREEN


class VolumeSubplot(Subplot):
    """Subplot for the volume indicator.

    Additional traces include:
    """
    def __init__(self):
        super().__init__('volume', [{"type": "bar"}], False)

    def get_subplot(self, df: DataFrame):
        """Builds the subplot.

        Args:
            df: The dataframe of simulation data.

        return:
            A plotly subplot.
        """
        df['volume_colors'] = np.where(df['color'] == 'red', BEAR_RED, BULL_GREEN)
        return fplt.Bar(
                    x=df['Date'],
                    y=df[self.data_symbol],
                    name='Volume',
                    marker_color=df['volume_colors'])

    def get_traces(self, df: DataFrame) -> list:
        """Build a list of traces to add to the subplot.

        Args:
            df: The dataframe of simulation data.

        return:
            list: A list of traces to add to the subplot defined in this class.
        """
        return []
