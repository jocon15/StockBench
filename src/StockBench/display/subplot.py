

class Subplot:
    def __init__(self, data_symbol, subplot_type):
        self.data_symbol = data_symbol
        self._TYPE = subplot_type

    def get_type(self):
        return self._TYPE
