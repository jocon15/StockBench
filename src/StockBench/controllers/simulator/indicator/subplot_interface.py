from abc import abstractmethod, ABC
from pandas import DataFrame
from typing import Union, Optional

from plotly.graph_objects import Scatter, Ohlc


class SubplotInterface(ABC):
    def __init__(self, data_symbol, subplot_type, is_ohlc_trace):
        self.data_symbol = data_symbol
        self._type = subplot_type
        self.__is_ohlc_trace = is_ohlc_trace

    def get_type(self):
        return self._type

    def is_ohlc_trace(self) -> bool:
        return self.__is_ohlc_trace

    @abstractmethod
    def get_subplot(self, df: DataFrame) -> Optional[Union[Scatter, Ohlc]]:
        raise NotImplementedError('Not implemented yet!')

    @abstractmethod
    def get_traces(self, df: DataFrame) -> list:
        raise NotImplementedError('Not implemented yet!')
