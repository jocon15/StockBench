import logging
from plotly.subplots import make_subplots
from StockBench.charting.charting_engine import ChartingEngine

log = logging.getLogger()


class SingularChartingEngine(ChartingEngine):
    """Charting tools for singular simulation analysis."""
    SUBPLOT_VERTICAL_SPACING = 0.05

    @staticmethod
    def build_indicator_chart(df, symbol, available_indicators, save_option=ChartingEngine.TEMP_SAVE) -> str:
        """Multi-plot chart for singular simulation indicators.

        Args:
            df (DataFrame): The full DataFrame post-simulation.
            symbol (str): The symbol the simulation was run on.
            available_indicators (any): The list of indicators.
            save_option (int): Save the chart.

        Return:
            (str): The filepath of the chart
        """
        subplot_objects = []
        subplot_types = []

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
            raise Exception('No OHLC indicator found, cannot chart!')

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

        # build the parent plot
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

        # update the layout
        window_size = len(df['Close'])
        if save_option != ChartingEngine.TEMP_SAVE:
            # non-temp save should show the simulation metadata in the title (uses DEFAULT margin)

            fig.update_layout(template='plotly_dark', title=f'{window_size} day simulation for {symbol}',
                              xaxis_rangeslider_visible=False)
        else:
            # temp save does not need a title because the data is shown elsewhere
            # setting xaxis_range prevents the buy and sell point traces from changing the chart scale
            # setting margin overrides plotly's default margin setting
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False,
                              xaxis_range=(df['Date'][0], df['Date'][window_size - 1]),
                              margin=dict(l=SingularChartingEngine.PLOTLY_CHART_MARGIN_LEFT,
                                          r=SingularChartingEngine.PLOTLY_CHART_MARGIN_RIGHT,
                                          t=SingularChartingEngine.PLOTLY_CHART_MARGIN_TOP,
                                          b=SingularChartingEngine.PLOTLY_CHART_MARGIN_BOTTOM))

        # format the chart (remove plotly white border)
        formatted_fig = ChartingEngine.format_chart(fig)

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, save_option,
                                                'temp_overview_chart', f'figure_{symbol}')

    @staticmethod
    def build_positions_duration_bar_chart(positions, symbol, save_option=ChartingEngine.TEMP_SAVE) -> str:
        """Builds a chart for singular duration of positions."""
        rows = 1
        cols = 1

        chart_list = [[{"type": "bar"}]]
        chart_titles = ('Duration per Position',)

        # Parent Plot
        fig = make_subplots(rows=rows,
                            cols=cols,
                            shared_xaxes=True,
                            vertical_spacing=0.15,
                            horizontal_spacing=0.05,
                            specs=chart_list,
                            subplot_titles=chart_titles)

        # positions analysis traces
        position_analysis_traces = ChartingEngine.positions_duration_bar(positions)

        # position analysis chart (overlayed traces)
        fig.add_trace(position_analysis_traces[0], 1, 1)
        fig.add_trace(position_analysis_traces[1], 1, 1)
        fig.add_trace(position_analysis_traces[2], 1, 1)

        # set the layout
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False)

        # format the chart (remove plotly white border)
        formatted_fig = ChartingEngine.format_chart(fig)

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, save_option,
                                                'temp_positions_duration_bar_chart', f'{symbol}_positions')

    @staticmethod
    def build_positions_profit_loss_bar_chart(positions, symbol, save_option=ChartingEngine.TEMP_SAVE) -> str:
        """Builds a chart for singular profit/loss of positions."""
        rows = 1
        cols = 1

        chart_list = [[{"type": "bar"}]]
        chart_titles = ('Total Profit/Loss per Position',)

        # Parent Plot
        fig = make_subplots(rows=rows,
                            cols=cols,
                            shared_xaxes=True,
                            vertical_spacing=0.15,
                            horizontal_spacing=0.05,
                            specs=chart_list,
                            subplot_titles=chart_titles)

        # positions analysis traces
        position_analysis_traces = ChartingEngine.positions_total_pl_bar(positions)

        # position analysis chart (overlayed traces)
        fig.add_trace(position_analysis_traces[0], 1, 1)
        fig.add_trace(position_analysis_traces[1], 1, 1)
        fig.add_trace(position_analysis_traces[2], 1, 1)

        # set the layout
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False)

        # format the chart (remove plotly white border)
        formatted_fig = ChartingEngine.format_chart(fig)

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, save_option,
                                                'temp_positions_profit_loss_bar_chart', f'{symbol}_positions')

    @staticmethod
    def build_positions_profit_loss_histogram_chart(strategy_name, positions, symbol, save_option=ChartingEngine.TEMP_SAVE) -> str:
        """Build a chart for positions histogram."""
        # put the strategy name inside a list so we can use it in the dataset histogram
        strategy_names = [strategy_name]
        positions_data = []

        data_list = []
        for position in positions:
            data_list.append(position.lifetime_profit_loss())
        positions_data.append(data_list)

        formatted_fig = ChartingEngine._build_multi_dataset_histogram(strategy_names, positions_data,
                                                                      'Position Profit/Loss Distribution per Strategy')

        # perform and saving or showing (returns saved filepath)
        return ChartingEngine.handle_save_chart(formatted_fig, ChartingEngine.TEMP_SAVE,
                                                'temp_positions_profit_loss_histogram_chart', f'')
