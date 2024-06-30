import statistics
import pandas as pd
from StockBench.display.display_constants import *
import plotly.graph_objects as plotter
from plotly.subplots import make_subplots
from StockBench.display.display import Display


class MultipleDisplay(Display):
    """This class defines a display object for a simulation where multiple stocks were simulated."""

    @staticmethod
    def chart_overview(data, save_option=Display.TEMP_SAVE) -> str:
        rows = 2
        cols = 2

        chart_list = [[{"type": "bar"}, {"type": "indicator"}], [{"type": "bar"}, {"type": "indicator"}]]
        chart_titles = ('Total Profit/Loss per Symbol ($)', '', 'Trades Made per Symbol', '')

        # Parent Plot
        fig = make_subplots(rows=rows,
                            cols=cols,
                            shared_xaxes=True,
                            vertical_spacing=0.15,
                            horizontal_spacing=0.05,
                            specs=chart_list,
                            subplot_titles=chart_titles)

        # Profit/Loss Bar
        fig.add_trace(MultipleDisplay.__overview_profit_loss_bar(data), row=1, col=1)

        # Avg Profit/Loss Gauge
        fig.add_trace(MultipleDisplay.__overview_avg_effectiveness_gauge(data), row=1, col=2)

        # Total Trades Made Bar
        fig.add_trace(MultipleDisplay.__overview_trades_made_bar(data), row=2, col=1)

        # Avg Profit/Loss Gauge
        fig.add_trace(MultipleDisplay.__overview_avg_profit_loss_gauge(data), row=2, col=2)

        # set the layout
        fig.update_layout(template='plotly_dark', title=f'Simulation Results for {len(data)} Symbols',
                          xaxis_rangeslider_visible=False, showlegend=False)

        # format the chart (remove plotly white border)
        formatted_fig = Display.format_chart(fig)

        # perform and saving or showing (returns saved filepath)
        return Display.handle_save_chart(formatted_fig, save_option, 'temp_overview_chart', 'multi')

    @staticmethod
    def chart_buy_rules_analysis(positions, save_option=Display.TEMP_SAVE) -> str:
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
        return Display.handle_save_chart(formatted_fig, save_option, 'temp_buy_chart', 'multi_buy_rules')

    @staticmethod
    def chart_sell_rules_analysis(positions, save_option=Display.TEMP_SAVE) -> str:
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

        # rule plpc stats chart (overlayed charts)
        rule_stats_traces = Display.rule_stats_traces(positions, 'sell')
        fig.add_trace(rule_stats_traces[0], 2, 1)
        fig.add_trace(rule_stats_traces[1], 2, 1)
        fig.add_trace(rule_stats_traces[2], 2, 1)

        # set the layout
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False)

        # format the chart (remove plotly white border)
        formatted_fig = Display.format_chart(fig)

        # perform and saving or showing (returns saved filepath)
        return Display.handle_save_chart(formatted_fig, save_option,
                                         'temp_sell_chart', 'multi_sell_rules')

    @staticmethod
    def chart_positions_analysis(positions, save_option=Display.TEMP_SAVE) -> str:
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
                                         'temp_positions_chart', 'multi_positions')

    @staticmethod
    def __overview_profit_loss_bar(data):
        color_df = pd.DataFrame()
        bar_colors = []
        for value in MultipleDisplay.__get_total_pl_per_symbol(data):
            if value > 0:
                bar_colors.append(BULL_GREEN)
            else:
                bar_colors.append(BEAR_RED)
        color_df['colors'] = bar_colors

        return plotter.Bar(
            x=MultipleDisplay.__get_symbols(data),
            y=MultipleDisplay.__get_total_pl_per_symbol(data),
            marker_color=color_df['colors'])

    @staticmethod
    def __overview_avg_effectiveness_gauge(data):
        indicator_value = MultipleDisplay.__get_avg_effectiveness(data)
        if indicator_value > 50.0:
            bar_color = 'green'
        else:
            bar_color = 'red'

        return plotter.Indicator(
            domain={'x': [0, 1], 'y': [0, 1]},
            value=indicator_value,
            number={"font": {"size": 55}},
            mode="gauge+number",
            title={'text': "Average Effectiveness Across all Trades (%)"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': bar_color},
                   'steps': [
                       {'range': [0, 50], 'color': PLOTLY_DARK_BACKGROUND},
                       {'range': [50, 100], 'color': PLOTLY_DARK_BACKGROUND}]})

    @staticmethod
    def __overview_avg_profit_loss_gauge(data):
        indicator_value = MultipleDisplay.__get_avg_pl(data)
        if indicator_value > 0:
            bar_color = 'green'
        else:
            bar_color = 'red'

        return plotter.Indicator(
            domain={'x': [0, 1], 'y': [0, 1]},
            value=indicator_value,
            number={"font": {"size": 55}},
            mode="gauge+number",
            title={'text': "Average Total Profit/Loss per Symbol ($)"},
            gauge={'axis': {'range': [-1000, 1000]},
                   'bar': {'color': bar_color},
                   'steps': [
                       {'range': [-1000, 0], 'color': PLOTLY_DARK_BACKGROUND},
                       {'range': [0, 1000], 'color': PLOTLY_DARK_BACKGROUND}]})

    @staticmethod
    def __overview_trades_made_bar(data):
        return plotter.Bar(
            x=MultipleDisplay.__get_symbols(data),
            y=MultipleDisplay.__get_trades_per_symbol(data),
            marker=dict(color=OFF_BLUE))

    @staticmethod
    def __get_symbols(data) -> list:
        return MultipleDisplay.__get_list_by_name('symbol', data)

    @staticmethod
    def __get_total_pl_per_symbol(data) -> list:
        return MultipleDisplay.__get_list_by_name('total_profit_loss', data)

    @staticmethod
    def __get_trades_per_symbol(data) -> list:
        return MultipleDisplay.__get_list_by_name('trades_made', data)

    @staticmethod
    def __get_avg_effectiveness(data) -> float:
        effectiveness_per_symbol = MultipleDisplay.__get_list_by_name('effectiveness', data)
        return round(float(statistics.mean(effectiveness_per_symbol)), 2)

    @staticmethod
    def __get_avg_pl(data) -> float:
        pl_per_symbol = MultipleDisplay.__get_list_by_name('total_profit_loss', data)
        return round(float(statistics.mean(pl_per_symbol)), 2)

    @staticmethod
    def __get_list_by_name(name, data) -> list:
        return [stock[name] for stock in data]

    @staticmethod
    def __list_out_of_100(value: float) -> list:
        if 0.0 >= value or value >= 100.0:
            raise ValueError(f'Value: {value} is out of range 0 - 100!')
        # place that number in the list x amount of times
        # result = [int(value) for _ in range(int(value))]
        # result += [0 for _ in range(100 - int(value))]
        result = [int(value), 100 - int(value)]
        return result
