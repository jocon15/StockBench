import logging
from typing import Tuple, List
from pandas import DataFrame
from plotly.subplots import make_subplots
from plotly.graph_objects import Figure

from StockBench.indicator.indicator import IndicatorInterface
from StockBench.charting.charting_engine import ChartingEngine
from StockBench.charting.exceptions import ChartingError

log = logging.getLogger()


class SingularChartingEngine(ChartingEngine):
    """Charting tools for singular simulation analysis."""
    SUBPLOT_VERTICAL_SPACING = 0.05

    DATE_COLUMN = 'Date'
    CLOSE_COLUMN = 'Close'

    @staticmethod
    def build_indicator_chart(df: DataFrame, symbol: str, available_indicators: List[IndicatorInterface],
                              save_option=ChartingEngine.TEMP_SAVE) -> str:
        """Multi-plot chart for singular simulation indicators.

        Args:
            df: The full DataFrame post-simulation.
            symbol: The symbol the simulation was run on.
            available_indicators: The list of indicators.
            save_option: Save the chart.

        Return:
            (str): The filepath of the chart
        """
        subplot_objects, subplot_types = SingularChartingEngine.__get_subplot_objects_and_types(df,
                                                                                                available_indicators)

        fig = SingularChartingEngine.__build_parent_figure(df, subplot_objects, subplot_types, available_indicators)

        formatted_fig = SingularChartingEngine.__update_layout(df, symbol, fig, save_option)

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, save_option,
                                                'temp_overview_chart', f'figure_{symbol}')

    @staticmethod
    def __get_subplot_objects_and_types(df: DataFrame,
                                        available_indicators: List[IndicatorInterface]) -> Tuple[list, list]:
        """"""
        subplot_objects = []
        subplot_types = []

        ohlc_indicator = SingularChartingEngine.__find_ohlc_indicator(available_indicators)

        # add ohlc to list
        subplot_objects.append(ohlc_indicator.get_subplot())

        # activate the subplot objects if evidence is found in the df
        for (column_name, column_data) in df.items():
            for indicator in available_indicators:
                indicator_subplot = indicator.get_subplot()
                if indicator_subplot is not None:
                    if column_name == indicator.get_data_name():
                        if not indicator_subplot.is_ohlc_trace():
                            # concatenate the 2 lists (add element to list)
                            subplot_objects = [x for n in (subplot_objects, [indicator_subplot]) for x in n]

        # get the subplot types after all subplot objects have been established
        for subplot in subplot_objects:
            subplot_types.append(subplot.get_type())

        return subplot_objects, subplot_types

    @staticmethod
    def __build_parent_figure(df, subplot_objects, subplot_types, available_indicators) -> Figure:
        """Build the parent plot"""
        cols = col = 1  # only one col in every row
        rows = len(subplot_objects)
        fig = make_subplots(rows=rows, cols=cols, shared_xaxes=True,
                            vertical_spacing=SingularChartingEngine.SUBPLOT_VERTICAL_SPACING, specs=subplot_types)

        # add subplots and traces from the objects to the parent plot
        for enum_row, subplot in enumerate(subplot_objects):
            row = enum_row + 1
            # add the subplot
            fig.add_trace(subplot.get_subplot(df), row=row, col=col)
            if subplot.get_type()[0]['type'] == 'ohlc':
                # special case for OHLC subplot
                traces = []
                # get the traces from the subplot
                for trace in subplot.get_traces(df):
                    traces.append(trace)
                # get the traces from all aux OHLC trace indicators
                for indicator in available_indicators:
                    indicator_subplot = indicator.get_subplot()
                    if indicator_subplot is not None:
                        if indicator_subplot.is_ohlc_trace():
                            for trace in indicator_subplot.get_traces(df):
                                traces.append(trace)
                # now add all traces to the subplot on the figure
                for trace in traces:
                    fig.add_trace(trace, row=row, col=col)
            else:
                # non-ohlc subplots
                # add the subplots traces to the subplot on the figure
                for trace in subplot.get_traces(df):
                    fig.add_trace(trace, row=row, col=col)

        return fig

    @staticmethod
    def __update_layout(df: DataFrame, symbol: str, fig: Figure, save_option: int) -> Figure:
        # update the layout
        window_size = len(df[SingularChartingEngine.CLOSE_COLUMN])
        if save_option != ChartingEngine.TEMP_SAVE:
            # non-temp save should show the simulation metadata in the title (uses DEFAULT margin)

            fig.update_layout(template='plotly_dark', title=f'{window_size} day simulation for {symbol}',
                              xaxis_rangeslider_visible=False)
        else:
            # temp save does not need a title because the data is shown elsewhere
            # setting xaxis_range prevents the buy and sell point traces from changing the chart scale
            # setting margin overrides plotly's default margin setting
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False,
                              xaxis_range=(df[SingularChartingEngine.DATE_COLUMN][0],
                                           df[SingularChartingEngine.DATE_COLUMN][window_size - 1]),
                              margin=dict(l=SingularChartingEngine.PLOTLY_CHART_MARGIN_LEFT,
                                          r=SingularChartingEngine.PLOTLY_CHART_MARGIN_RIGHT,
                                          t=SingularChartingEngine.PLOTLY_CHART_MARGIN_TOP,
                                          b=SingularChartingEngine.PLOTLY_CHART_MARGIN_BOTTOM))

        # format the chart (remove plotly white border)
        formatted_fig = ChartingEngine.format_chart(fig)

        return formatted_fig

    @staticmethod
    def __find_ohlc_indicator(available_indicators: List[IndicatorInterface]):
        """"""
        # find the OHLC indicator
        ohlc_indicator = None
        for indicator in available_indicators:
            indicator_subplot = indicator.get_subplot()
            if indicator_subplot is not None:
                try:
                    if indicator_subplot.get_type()[0]['type'] == 'ohlc':
                        ohlc_indicator = indicator
                        break
                except (KeyError, TypeError):
                    continue

        if not ohlc_indicator:
            raise ChartingError('No OHLC indicator found, cannot chart!')

        return ohlc_indicator
