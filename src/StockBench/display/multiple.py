import os
import statistics
from .display_constants import *
import plotly.graph_objects as fplt
from plotly.subplots import make_subplots
from StockBench.function_tools.nonce import datetime_nonce


class MultipleDisplay:

    def __init__(self):
        self.__data = None

    def chart(self, data):
        self.__data = data

        rows = 2
        cols = 2

        chart_list = [[{"type": "bar"}, {"type": "indicator"}], [{"type": "bar"}, {"type": "indicator"}]]
        chart_titles = ('Profit/Loss($)', '', 'Trades Made', '')

        # Parent Plot
        fig = make_subplots(rows=rows,
                            cols=cols,
                            shared_xaxes=True,
                            vertical_spacing=0.1,
                            horizontal_spacing=0.01,
                            specs=chart_list,
                            subplot_titles=chart_titles)

        # Profit/Loss Bar Chart
        fig.add_trace(fplt.Bar(x=self.__get_symbols(), y=self.__get_total_pl_per_symbol(),
                               marker=dict(color=BULL_GREEN)), row=1, col=1)

        # for the pie chart (avg effectiveness)
        # effectiveness = self.__get_avg_effectiveness()
        # values = self.__list_out_of_100(effectiveness)
        # fig.add_trace(fplt.Pie(values=values), row=1, col=2)

        indicator_value = self.__get_avg_effectiveness()
        if indicator_value > 0:
            bar_color = 'green'
        else:
            bar_color = 'red'

        fig.add_trace(fplt.Indicator(
            domain={'x': [0, 1], 'y': [0, 1]},
            value=indicator_value,
            mode="gauge+number+delta",
            title={'text': "Global Average Effectiveness(%)"},
            # delta={'reference': 0},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': bar_color},
                   'steps': [
                       {'range': [0, 50], 'color': "grey"},
                       {'range': [50, 100], 'color': "darkgrey"}]}),
            row=1, col=2)

        # for the bar (total trades made)
        #   this could be stacked so you can visualize it better
        fig.add_trace(fplt.Bar(x=self.__get_symbols(), y=self.__get_trades_per_symbol(),
                               marker=dict(color=OFF_BLUE)), row=2, col=1)
        # fig.update_traces(marker_color=BULL_GREEN, selector=dict(type='bar'))
        # fig.update_traces(name='volume', selector=dict(type='bar'))

        # for the dial
        # fig.add_trace(fplt.Barpolar(theta=[0, 45, 90], r=[2, 3, 1]), row=1, col=2)

        indicator_value = self.__get_avg_pl()
        if indicator_value > 0:
            bar_color = 'green'
        else:
            bar_color = 'red'

        fig.add_trace(fplt.Indicator(
            domain={'x': [0, 1], 'y': [0, 1]},
            value=indicator_value,
            mode="gauge+number+delta",
            title={'text': "Global Average Profit/Loss($)"},
            # delta={'reference': 0},
            gauge={'axis': {'range': [-1000, 1000]},
                   'bar': {'color': bar_color},
                   'steps': [
                       {'range': [-1000, 0], 'color': "grey"},
                       {'range': [0, 1000], 'color': "darkgrey"}]}),
            row=2, col=2)

        fig.update_layout(template='plotly_dark', title=f'Simulation Results for {len(self.__data)} Symbols',
                          xaxis_rangeslider_visible=False, showlegend=False)

        chart_filepath = os.path.join('display', f'display_{datetime_nonce()}.html')
        # make the directories if they don't already exist
        os.makedirs(os.path.dirname(chart_filepath), exist_ok=True)

        fig.write_html(chart_filepath, auto_open=True)

    def __get_symbols(self) -> list:
        return self.__get_list_by_name('symbol')

    def __get_total_pl_per_symbol(self) -> list:
        return self.__get_list_by_name('total_profit_loss')

    def __get_trades_per_symbol(self) -> list:
        return self.__get_list_by_name('trades_made')

    def __get_avg_effectiveness(self) -> float:
        effectiveness_per_symbol = self.__get_list_by_name('effectiveness')
        return round(float(statistics.mean(effectiveness_per_symbol)), 2)

    def __get_avg_pl(self) -> float:
        pl_per_symbol = self.__get_list_by_name('total_profit_loss')
        return round(float(statistics.mean(pl_per_symbol)), 2)

    def __get_list_by_name(self, name) -> list:
        return [stock[name] for stock in self.__data]

    @staticmethod
    def __list_out_of_100(value: float) -> list:
        if 0.0 >= value or value >= 100.0:
            raise ValueError(f'Value: {value} is out of range 0 - 100!')
        # place that number in the list x amount of times
        # result = [int(value) for _ in range(int(value))]
        # result += [0 for _ in range(100 - int(value))]
        result = [int(value), 100 - int(value)]
        return result
