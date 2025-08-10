import logging
from typing import Tuple, List
from pandas import DataFrame
from plotly.subplots import make_subplots
from plotly.graph_objects import Figure
import plotly.graph_objects as plotter

from StockBench.indicator.indicator import IndicatorInterface
from StockBench.indicator.subplot import Subplot
from StockBench.indicators.volume.subplot import VolumeSubplot
from StockBench.charting.charting_engine import ChartingEngine
from StockBench.charting.exceptions import ChartingError
from StockBench.charting.display_constants import *

log = logging.getLogger()


class VolumeNotFoundException(Exception):
    pass


class SingularChartingEngine(ChartingEngine):
    """Charting tools for singular simulation analysis."""
    SUBPLOT_VERTICAL_SPACING = 0.05

    DATE_COLUMN = 'Date'
    CLOSE_COLUMN = 'Close'

    @staticmethod
    def build_indicator_chart(df: DataFrame, symbol: str, available_indicators: List[IndicatorInterface],
                              show_volume: bool,
                              save_option=ChartingEngine.TEMP_SAVE) -> str:
        """Multi-plot chart for singular simulation indicators."""
        subplot_objects, subplot_types = SingularChartingEngine.__get_subplot_objects_and_types(df,
                                                                                                available_indicators)

        fig = SingularChartingEngine.__build_parent_figure(df, subplot_objects, subplot_types, available_indicators,
                                                           show_volume)

        formatted_fig = SingularChartingEngine.__update_layout(df, symbol, fig, save_option)

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, save_option,
                                                'temp_overview_chart', f'figure_{symbol}')

    @staticmethod
    def build_account_value_line_chart(df: DataFrame, symbol: str, save_option=ChartingEngine.TEMP_SAVE) -> str:
        """Builds a chart for duration of positions.

        return:
            str: The filepath of the built chart.
        """
        rows = 1
        cols = 1

        chart_list = [[{"type": "scatter"}]]
        chart_titles = ('Account Value',)

        # Parent Plot
        fig = make_subplots(rows=rows,
                            cols=cols,
                            shared_xaxes=True,
                            vertical_spacing=0.15,
                            horizontal_spacing=0.05,
                            specs=chart_list,
                            subplot_titles=chart_titles)

        # positions analysis traces
        bar_chart_trace = plotter.Scatter(y=df['Account Value'], marker=dict(color=OFF_BLUE), fill='tozeroy',
                                          name='Account Value')

        # position analysis chart (overlaid traces)
        fig.add_trace(bar_chart_trace, 1, 1)
        fig.add_hline(y=df['Account Value'][0], line_width=1, line_dash="dash", line_color='white')

        # set the layout
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, xaxis_title='Simulation Day',
                          yaxis_title='Account Value ($)')

        # format the chart (remove plotly white border)
        formatted_fig = ChartingEngine.format_chart(fig)

        temp_filename = 'temp_account_value_line_chart'
        unique_prefix = f'{symbol}_account_value_line_chart'

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, save_option, temp_filename, unique_prefix)

    @staticmethod
    def __get_subplot_objects_and_types(df: DataFrame,
                                        available_indicators: List[IndicatorInterface]) -> Tuple[list, list]:
        """Builds a list of subplots objects and a list of subplot types."""
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
    def __build_parent_figure(df: DataFrame, subplot_objects: List[Subplot], subplot_types: List[List],
                              available_indicators: List[IndicatorInterface], show_volume: bool) -> Figure:
        """Builds the parent figure."""
        if not show_volume:
            subplot_objects, subplot_types = SingularChartingEngine.__remove_volume_subplot(subplot_objects,
                                                                                            subplot_types)

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

    @staticmethod
    def __remove_volume_subplot(subplot_objects: List[Subplot], subplot_types: List[List]) -> tuple:
        for index, subplot in enumerate(subplot_objects):
            if type(subplot) is VolumeSubplot:
                # remove the volume subplot and the volume subplot type
                subplot_objects.pop(index)
                subplot_types.pop(index)
                return subplot_objects, subplot_types
        raise VolumeNotFoundException('A volume subplot was not provided in the data')
