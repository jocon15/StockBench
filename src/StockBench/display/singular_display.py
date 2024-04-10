import logging
from plotly.subplots import make_subplots
from StockBench.display.display import Display

log = logging.getLogger()


class SingularDisplay(Display):
    """This class defines a display object.

    The display object is used as an API for the simulator to chart the data. The display will use the simulation
    data to establish which subplots need to be added to the singular chart. The subplots abstract all of that
    specific subplots details to make it easier to edit. This API simply aggregates the subplot objects and
    assembles the final parent plot that gets displayed to the user.
    """
    def __init__(self, indicators):
        self.__df = None

        self.__indicators = indicators

        # DO NOT ADD ANY to this list
        self.__subplot_objects = []
        self.__subplot_types = []

    def chart_overview(self, df, symbol, show=True, save_option=Display.TEMP_SAVE) -> str:
        """Chart the data.

        Args:
            df (DataFrame): The full DataFrame post-simulation.
            symbol (str): The symbol the simulation was run on.
            show (bool): Show the chart.
            save_option (int): Save the chart.

        Return:
            (str): The filepath of the chart
        """
        self.__df = df

        # find the OHLC indicator
        ohlc_indicator = None
        for indicator in self.__indicators:
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
        self.__subplot_objects.append(ohlc_indicator.get_subplot())

        # activate the subplot objects if evidence is found in the df
        for (column_name, column_data) in self.__df.items():
            for indicator in self.__indicators:
                indicator_subplot = indicator.get_subplot()
                if indicator_subplot is not None:
                    if column_name == indicator.get_data_name():
                        if not indicator_subplot.is_ohlc_trace():
                            # concatenate the 2 lists (add element to list)
                            self.__subplot_objects = [x for n in (self.__subplot_objects, [indicator_subplot]) for x in
                                                      n]

        # get the subplot types after all subplot objects have been established
        for subplot in self.__subplot_objects:
            self.__subplot_types.append(subplot.get_type())

        # build the parent plot
        cols = col = 1  # only one col in every row
        rows = len(self.__subplot_objects)
        fig = make_subplots(rows=rows, cols=cols, shared_xaxes=True, vertical_spacing=0.06, specs=self.__subplot_types)

        # add subplots and traces from the objects to the parent plot
        for enum_row, subplot in enumerate(self.__subplot_objects):
            row = enum_row + 1
            # add the subplot
            fig.add_trace(subplot.get_subplot(self.__df), row=row, col=col)
            if subplot.get_type()[0]['type'] == 'ohlc':
                # special case for OHLC subplot
                traces = []
                # get the traces from the subplot
                for trace in subplot.get_traces(self.__df):
                    traces.append(trace)
                # get the traces from all aux OHLC trace indicators
                for indicator in self.__indicators:
                    indicator_subplot = indicator.get_subplot()
                    if indicator_subplot is not None:
                        if indicator_subplot.is_ohlc_trace():
                            for trace in indicator_subplot.get_traces(self.__df):
                                traces.append(trace)
                # now add all traces to the subplot on the figure
                for trace in traces:
                    fig.add_trace(trace, row=row, col=col)
            else:
                # non-ohlc subplots
                # add the subplots traces to the subplot on the figure
                for trace in subplot.get_traces(self.__df):
                    fig.add_trace(trace, row=row, col=col)

        # update the layout
        window_size = len(self.__df['Close'])
        fig.update_layout(template='plotly_dark', title=f'{window_size} day simulation for {symbol}',
                          xaxis_title='Date', yaxis_title='Price (USD)', xaxis_rangeslider_visible=False)

        # format the chart (remove plotly white border)
        formatted_fig = Display.format_chart(fig)

        # perform and saving or showing (returns saved filepath)
        return self.handle_save_chart(formatted_fig, show, save_option,
                                      'temp_chart', f'figure_{symbol}')

    def chart_buy_rules_analysis(self, positions, symbol, show=True, save_option=Display.TEMP_SAVE) -> str:
        rows = 1
        cols = 1

        chart_list = [[{"type": "bar"}]]
        chart_titles = ('Acquisition count per rule',)

        # Parent Plot
        fig = make_subplots(rows=rows,
                            cols=cols,
                            shared_xaxes=True,
                            vertical_spacing=0.15,
                            horizontal_spacing=0.05,
                            specs=chart_list,
                            subplot_titles=chart_titles)

        fig.add_trace(Display.buy_rule_count_bar(positions))

        # set the layout
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, showlegend=False)

        # format the chart (remove plotly white border)
        formatted_fig = Display.format_chart(fig)

        # perform and saving or showing (returns saved filepath)
        return self.handle_save_chart(formatted_fig, show, save_option,
                                      'temp_buy_chart', f'{symbol}_buy_rules')

    def chart_sell_rules_analysis(self, positions, symbol, show=True, save_option=Display.TEMP_SAVE) -> str:
        rows = 1
        cols = 1

        chart_list = [[{"type": "bar"}]]
        chart_titles = ('Acquisition count per rule',)

        # Parent Plot
        fig = make_subplots(rows=rows,
                            cols=cols,
                            shared_xaxes=True,
                            vertical_spacing=0.15,
                            horizontal_spacing=0.05,
                            specs=chart_list,
                            subplot_titles=chart_titles)

        fig.add_trace(Display.sell_rule_count_bar(positions))

        # set the layout
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, showlegend=False)

        # format the chart (remove plotly white border)
        formatted_fig = Display.format_chart(fig)

        # perform and saving or showing (returns saved filepath)
        return self.handle_save_chart(formatted_fig, show, save_option,
                                      'temp_sell_chart', f'{symbol}_se;;_rules')
