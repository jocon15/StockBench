import logging
from plotly.subplots import make_subplots
from StockBench.display.display import Display

log = logging.getLogger()


class SingularDisplay(Display):
    """This class defines a display object for a simulation where a single stock was simulated.

    The display object is used as an API for the simulator to chart the data. The display will use the simulation
    data to establish which subplots need to be added to the singular chart. The subplots abstract all of that
    specific subplots details to make it easier to edit. This API simply aggregates the subplot objects and
    assembles the final parent plot that gets displayed to the user.
    """
    SUBPLOT_VERTICAL_SPACING = 0.05

    @staticmethod
    def chart_overview(df, symbol, available_indicators, save_option=Display.TEMP_SAVE) -> str:
        """Chart the data.

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
                            vertical_spacing=SingularDisplay.SUBPLOT_VERTICAL_SPACING, specs=subplot_types)

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
        if save_option != Display.TEMP_SAVE:
            # non-temp save should show the simulation metadata in the title (uses DEFAULT margin)

            fig.update_layout(template='plotly_dark', title=f'{window_size} day simulation for {symbol}',
                              xaxis_rangeslider_visible=False)
        else:
            # temp save does not need a title because the data is shown elsewhere
            # setting xaxis_range prevents the buy and sell point traces from changing the chart scale
            # setting margin overrides plotly's default margin setting
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False,
                              xaxis_range=(df['Date'][0], df['Date'][window_size - 1]),
                              margin=dict(l=SingularDisplay.PLOTLY_CHART_MARGIN_LEFT,
                                          r=SingularDisplay.PLOTLY_CHART_MARGIN_RIGHT,
                                          t=SingularDisplay.PLOTLY_CHART_MARGIN_TOP,
                                          b=SingularDisplay.PLOTLY_CHART_MARGIN_BOTTOM))

        # format the chart (remove plotly white border)
        formatted_fig = Display.format_chart(fig)

        # perform and saving or showing (returns saved filepath)
        return Display.handle_save_chart(formatted_fig, save_option,
                                         'temp_overview_chart', f'figure_{symbol}')

    @staticmethod
    def chart_buy_rules_analysis(positions, symbol, save_option=Display.TEMP_SAVE) -> str:
        rows = 2
        cols = 1

        chart_list = [[{"type": "bar"}], [{"type": "bar"}]]
        chart_titles = ('Acquisition Count per Rule', 'Position Profit/Loss % Analytics per Acquisition Rule')

        # Parent Plot
        fig = make_subplots(rows=rows,
                            cols=cols,
                            shared_xaxes=True,
                            vertical_spacing=0.15,
                            horizontal_spacing=0.05,
                            specs=chart_list,
                            subplot_titles=chart_titles)

        # rule counts chart
        fig.add_trace(Display.rule_count_bar(positions, 'buy'), 1, 1)

        # rule plpc stats chart (overlayed charts)
        rule_stats_traces = Display.rule_stats_traces(positions, 'buy')
        fig.add_trace(rule_stats_traces[0], 2, 1)
        fig.add_trace(rule_stats_traces[1], 2, 1)
        fig.add_trace(rule_stats_traces[2], 2, 1)

        # set the layout
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False)

        # format the chart (remove plotly white border)
        formatted_fig = Display.format_chart(fig)

        # perform and saving or showing (returns saved filepath)
        return Display.handle_save_chart(formatted_fig, save_option,
                                         'temp_buy_chart', f'{symbol}_buy_rules')

    @staticmethod
    def chart_sell_rules_analysis(positions, symbol, save_option=Display.TEMP_SAVE) -> str:
        rows = 2
        cols = 1

        chart_list = [[{"type": "bar"}], [{"type": "bar"}]]
        chart_titles = ('Liquidation Count per Rule', 'Position Profit/Loss % Analytics per Liquidation Rule')

        # Parent Plot
        fig = make_subplots(rows=rows,
                            cols=cols,
                            shared_xaxes=True,
                            vertical_spacing=0.15,
                            horizontal_spacing=0.05,
                            specs=chart_list,
                            subplot_titles=chart_titles)

        # rule counts chart
        fig.add_trace(Display.rule_count_bar(positions, 'sell'), 1, 1)

        # rule plpc stats chart (overlayed traces)
        rule_stats_traces = Display.rule_stats_traces(positions, 'sell')
        fig.add_trace(rule_stats_traces[0], 2, 1)
        fig.add_trace(rule_stats_traces[1], 2, 1)
        fig.add_trace(rule_stats_traces[2], 2, 1)

        # set the layout
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False)

        # format the chart (remove plotly white border)
        formatted_fig = Display.format_chart(fig)

        # perform and saving or showing (returns saved filepath)
        return Display.handle_save_chart(formatted_fig, save_option, 'temp_sell_chart', f'{symbol}_sell_rules')

    @staticmethod
    def chart_positions_analysis(positions, symbol, save_option=Display.TEMP_SAVE) -> str:
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
        position_analysis_traces = Display.positions_total_pl_bar(positions)

        # position analysis chart (overlayed traces)
        fig.add_trace(position_analysis_traces[0], 1, 1)
        fig.add_trace(position_analysis_traces[1], 1, 1)
        fig.add_trace(position_analysis_traces[2], 1, 1)

        # set the layout
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False)

        # format the chart (remove plotly white border)
        formatted_fig = Display.format_chart(fig)

        # perform and saving or showing (returns saved filepath)
        return Display.handle_save_chart(formatted_fig, save_option,
                                         'temp_positions_chart', f'{symbol}_positions')
