import statistics
from StockBench.function_tools.function_wrappers import performance_timer


class Indicators:
    """This class defines an indicators object.

    The indicators object is used as an API for the simulator to use to calculate values for indicators. For example,
    the simulation will likely require an indicator like SMA, in which case the simulation needs the values of SMA
    for every day in the simulation.

    The simulator will pass the relevant data needed for the calculation to the dedicated function in this API. The
    specific function will then return the calculated values for that indicator. The simulator adds that data to the
    DataFrame prior to the simulation.

    The simulator is designed to request additional data beyond the simulation window to have accurate indicator data
    day 1 of the simulation window. Because we've done that, the first few calculated values of these indicators will
    be incorrect (as expected) due to too small sample size. Since the simulator has requested additional data, the
    incorrect early indicator values will get cut off by the simulation window. Essentially, the indicator data will
    be accurate by the time the simulation starts and the data will be accurate throughout the simulation.

    ****************************************************************************************************************
        If you're adding an indicator, make sure that you add the correct amount of additional days needed in the
        __parse_strategy_timestamps() function in the simulator class.
    ****************************************************************************************************************

    """
    @staticmethod
    @performance_timer
    def candle_color(open_data: list, close_data: list) -> list:
        """ Calculate the color of a candle on a given day.

        Args:
            open_data (list): The open price data.
            close_data (list): The close price data.

        return:
            list: the colors that correspond to the candles
        """
        if len(open_data) != len(close_data):
            raise Exception('Data list lengths must match!')

        colors = list()
        for i in range(len(open_data)):
            if float(close_data[i]) > float(open_data[i]):
                colors.append('green')
            else:
                colors.append('red')

        return colors

    @staticmethod
    @performance_timer
    def SMA(length: int, price_data: list) -> list:
        """Calculate the RSI values for a list of price values.

        Args:
            length (int): The length of the SMA to calculate.
            price_data (list): The price data to calculate the RSI from.

        return:
            list: The list of calculated SMA values.
        """
        price_values = list()
        sma_values = list()
        all_sma_values = list()
        for element in price_data:
            if len(price_values) < length:
                price_values.append(float(element))
            else:
                price_values.pop(0)
                sma_values.pop(0)
                price_values.append(float(element))
            avg = round(statistics.mean(price_values), 3)
            sma_values.append(avg)
            all_sma_values.append(avg)
        return all_sma_values

    @staticmethod
    @performance_timer
    def RSI(length: int, price_data: list) -> list:
        """Calculate the RSI values for a list of price values.

        Args:
            length (int): The length of the RSI to calculate.
            price_data (list): The price data to calculate the RSI from.

        return:
            list: The list of calculated RSI values.
        """
        first_day_value = 0
        gain = []
        loss = []
        rsi = []
        all_rsi = list()  # archive to return
        for i in range(1, len(price_data)):
            dif = float(price_data[i]) - float(price_data[i - 1])
            if dif > 0:
                if len(gain) == length:
                    gain.pop(0)
                    gain.append(dif)
                else:
                    gain.append(dif)
            elif dif < 0:
                if len(loss) == length:
                    loss.pop(0)
                    loss.append(abs(dif))
                else:
                    loss.append(abs(dif))
            if len(gain) > 0 and len(loss) > 0:
                avg_gain = statistics.mean(gain)
                avg_loss = statistics.mean(loss)
                rs = avg_gain / avg_loss
                rs_index = round(100 - (100 / (1 + rs)), 3)
                if len(rsi) == 6:
                    rsi.pop(0)
                    rsi.append(rs_index)
                else:
                    rsi.append(rs_index)
                if i == 1:
                    first_day_value = rs_index
                all_rsi.append(rs_index)

        # ensure that the data returned is the same size
        # **
        # Note: Given that the simulation has additional days,
        # the days that these values are assigned to will not be seen
        # by the simulation
        # **
        if len(all_rsi) != len(price_data):
            dif = len(price_data) - len(all_rsi)
            for _ in range(dif):
                # append initial values to the front of the list
                all_rsi.insert(0, first_day_value)

        return all_rsi

    @staticmethod
    @performance_timer
    def stochastic_oscillator(length: int, high_data: list, low_data: list, close_data: list) -> list:
        """Calculate the RSI values for a list of price values.

        Args:
            length (int): The length of the stochastic oscillator to calculate.
            high_data (list): The high price data to calculate the stochastic oscillator from.
            low_data (list): The high price data to calculate the stochastic oscillator from.
            close_data (list): The close price data to calculate the stochastic oscillator from.

        return:
            list: The list of calculated RSI values.
        """
        past_length_days_high = list()
        past_length_days_low = list()
        past_length_days_close = list()
        stochastic_oscillator = list()
        for i in range(len(close_data)):
            if i < length:
                past_length_days_high.append(float(high_data[i]))
                past_length_days_low.append(float(low_data[i]))
                past_length_days_close.append(float(close_data[i]))
            else:
                past_length_days_high.pop(0)
                past_length_days_low.pop(0)
                past_length_days_close.pop(0)
                past_length_days_high.append(float(high_data[i]))
                past_length_days_low.append(float(low_data[i]))
                past_length_days_close.append(float(close_data[i]))

            stochastic_oscillator.append(((float(close_data[i]) - min(past_length_days_low)) /
                                          (max(past_length_days_high) - min(past_length_days_low))) * 100.0)

        return stochastic_oscillator
