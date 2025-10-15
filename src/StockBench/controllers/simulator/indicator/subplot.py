from abc import abstractmethod
from pandas import DataFrame


class Subplot:
    def __init__(self, data_symbol, subplot_type, is_ohlc_trace):
        self.data_symbol = data_symbol
        self._type = subplot_type
        self.__is_ohlc_trace = is_ohlc_trace

    def get_type(self):
        return self._type

    def is_ohlc_trace(self):
        return self.__is_ohlc_trace

    @abstractmethod
    def get_subplot(self, df: DataFrame):
        raise NotImplementedError('Not implemented yet!')

    @abstractmethod
    def get_traces(self, df: DataFrame):
        raise NotImplementedError('Not implemented yet!')
