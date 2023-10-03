from abc import abstractmethod


class PluginInterface:
    @abstractmethod
    def get_strategy_name(self):
        raise NotImplementedError('Not implemented yet!')

    @abstractmethod
    def get_data_name(self):
        raise NotImplementedError('Not implemented yet!')

    @abstractmethod
    def get_trigger(self):
        raise NotImplementedError('Not implemented yet!')

    @abstractmethod
    def get_subplot(self):
        raise NotImplementedError('Not implemented yet!')
