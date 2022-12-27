import pandas as pd
import statistics


class Indicators:
    def __init__(self, _data: pd.DataFrame):
        self.__data = _data

    def candle_color(self, _current_day_index: int) -> int:
        """ Calculate the color of a candle on a given day.

        Args:
            _current_day_index (int): The index of the current date to get the candle color at.

        return:
            int: The color of the candle on that day (0 -> red) (1 -> green).
        """
        if _current_day_index < 0:
            raise Exception('Current day index is out of bounds (less than 0)')

        open_price = self.__data['Open'][_current_day_index]
        close_price = self.__data['Close'][_current_day_index]
        if close_price >= open_price:
            return 1
        return 0

    def SMA(self, _length: int, _current_day_index: int) -> float:
        """ Calculate Simple Moving Average (SMA) of Any Length.

        Args:
            _length (int): Moving average length in days.
            _current_day_index (int): The index of the current date to calculate SMA at.

        return:
            float: The SMA value at the current day.
        """
        starting_day_index = _current_day_index - _length
        if starting_day_index < 0:
            raise Exception('Insufficient data to calculate SMA')

        price_values = list()
        sma_values = list()
        for current_day_index in range(_length):
            if len(price_values) < _length:
                price_values.append(float(self.__data['Close'][current_day_index]))
                avg = round(statistics.mean(price_values), 3)
                sma_values.append(avg)
            else:
                price_values.pop(0)
                sma_values.pop(0)
                price_values.append(float(self.__data['Close'][current_day_index]))
                avg = round(statistics.mean(price_values), 3)
                sma_values.append(avg)
        return sma_values[-1]

    def RSI(self, _length: int, _current_day_index: int) -> float:
        """ Calculate the Relative Strength Index (RSI) of Any Length.

        Args:
            _length (int): Index length in days.
            _current_day_index (int): The index of the current date to calculate RSI at.

        return:
            float: The RSI value at the current day.
        """
        starting_day_index = _current_day_index - _length
        if starting_day_index < 0:
            raise Exception('Insufficient data to calculate RSI')

        gain = []
        loss = []
        rsi = []
        for current_day_index in range(1, _length):
            dif = self.__data['Close'][current_day_index] - self.__data['Close'][current_day_index - 1]
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
        return rsi[-1]
