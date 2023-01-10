import pandas as pd
import statistics


class Indicators:

    def __init__(self):
        self.__data = None

    def add_data(self, _data: pd.DataFrame):
        """Supply the object with data"""
        self.__data = _data

    def candle_color(self, _current_day_index: int) -> int:
        """ Calculate the color of a candle on a given day.

        Args:
            _current_day_index (int): The index of the current date to get the candle color at.

        return:
            int: The color of the candle on that day (0 -> red) (1 -> green).
        """
        if self.__data.empty:
            raise Exception('Data must be supplied to the object first using add_data().')
        if _current_day_index < 0:
            raise Exception('Current day index is out of bounds (less than 0)')

        open_price = self.__data['Open'][_current_day_index]
        close_price = self.__data['Close'][_current_day_index]
        if close_price >= open_price:
            return 1
        return 0

    @staticmethod
    def SMA(_length: int, _data: list) -> list:
        """Calculate the RSI values for a list of price values.

        Args:
            _length (int): The length of the SMA to calculate.
            _data (list): The price data to calculate the RSI from.

        return:
            list: The list of calculated SMA values.
        """
        price_values = list()
        sma_values = list()
        all_sma_values = list()
        for element in _data:
            if len(price_values) < _length:
                price_values.append(float(element))
                avg = round(statistics.mean(price_values), 3)
                sma_values.append(avg)
                all_sma_values.append(avg)
            else:
                price_values.pop(0)
                sma_values.pop(0)
                price_values.append(float(element))
                avg = round(statistics.mean(price_values), 3)
                sma_values.append(avg)
                all_sma_values.append(avg)
        return all_sma_values

    @staticmethod
    def RSI(_length: int, _data: list) -> list:
        """Calculate the RSI values for a list of price values.

        Args:
            _length (int): The length of the RSI to calculate.
            _data (list): The price data to calculate the RSI from.

        return:
            list: The list of calculated RSI values.
        """
        first_day_value = 0
        gain = []
        loss = []
        rsi = []
        all_rsi = list()  # archive to return
        for i in range(1, len(_data)):
            dif = _data[i] - _data[i - 1]
            if dif > 0:
                if len(gain) == _length:
                    gain.pop(0)
                    gain.append(dif)
                else:
                    gain.append(dif)
            elif dif < 0:
                if len(loss) == _length:
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
        if len(all_rsi) != len(_data):
            dif = len(_data) - len(all_rsi)
            for _ in range(dif):
                # append initial values to the front of the list
                all_rsi.insert(0, first_day_value)

        return all_rsi
