from abc import abstractmethod


class IndicatorInterface:
    @property
    @abstractmethod
    def strategy_name(self):
        raise NotImplementedError('Not implemented yet!')

    @property
    @abstractmethod
    def data_name(self):
        raise NotImplementedError('Not implemented yet!')

    @property
    @abstractmethod
    def trigger(self):
        raise NotImplementedError('Not implemented yet!')

    @property
    @abstractmethod
    def subplot(self):
        raise NotImplementedError('Not implemented yet!')
