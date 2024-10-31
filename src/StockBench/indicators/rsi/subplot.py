import plotly.graph_objects as fplt
from StockBench.indicator.subplot import Subplot
from StockBench.charting.display_constants import WHITE, HORIZONTAL_TRIGGER_YELLOW


class RSISubplot(Subplot):
    """This class is a subclass of the Subplot class.

    An RSI object contains the subplot with RSI data.

    Additional traces include:
        - RSI upper algorithm
        - RSI lower algorithm
    """

    def __init__(self):
        super().__init__('RSI', [{"type": "scatter"}], False)

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
        traces = []
        for (column_name, column_data) in df.items():
            # RSI + underscore indicates it is an RSI trigger value
            if 'RSI_' in column_name:
                traces.append(fplt.Scatter(
                    x=df['Date'],
                    y=df[column_name],
                    line=dict(color=HORIZONTAL_TRIGGER_YELLOW),
                    name=column_name))

        return traces
