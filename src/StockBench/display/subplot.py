from abc import abstractmethod


class Subplot:
    def __init__(self, data_symbol, subplot_type, is_ohlc_trace):
        self.data_symbol = data_symbol
        self._TYPE = subplot_type
        self.__is_ohlc_trace = is_ohlc_trace

    def get_type(self):
        return self._TYPE

    def is_OHLC_trace(self):
        return self.__is_ohlc_trace

    @staticmethod
    @abstractmethod
    def get_subplot(df):
        raise NotImplementedError('Not implemented yet!')

    @staticmethod
    @abstractmethod
    def get_traces(self):
        raise NotImplementedError('Not implemented yet!')
