from typing import Union

from pandas import DataFrame


class DataManager:
    """Encapsulates an interface that wraps the core simulation data."""
    CLOSE = 'Close'
    OPEN = 'Open'
    HIGH = 'High'
    LOW = 'Low'
    VOLUME = 'volume'
    COLOR = 'color'

    def __init__(self, data):
        self.__df = data
        self.__add_candle_colors()

    def add_column(self, name: str, data: list):
        """Adds a list of data as a column in the DataFrame."""
        if type(name) is not str:
            raise Exception('New column name must be a string!')
        if type(data) is not list:
            raise Exception('New column data must be a list!')
        for col_name in self.get_column_names():
            if name == col_name:
                # a column with that name already exists, skip
                return

        self.__df[name] = data

    def get_data_length(self) -> int:
        """Gets the length of the DataFrame."""
        return len(self.__df[self.CLOSE])

    def get_column_names(self) -> list:
        """Gets the names of the columns in the DataFrame."""
        col_names = []
        for (col_name, col_vals) in self.__df.items():
            col_names.append(col_name)
        return col_names

    def get_data_point(self, column_name: str, current_day_index: int) -> Union[str, int, float, None]:
        """Gets a single data point from the DataFrame."""
        if type(column_name) is not str:
            raise Exception('Column name must be a string!')
        if type(current_day_index) is not int:
            raise Exception('Day index must be an integer!')
        return self.__df[column_name][current_day_index]

    def get_multiple_data_points(self, name: str, current_day_index: int, num_points: int) -> list:
        """Gets multiple data points from the DataFrame."""
        return_values = []
        for i in range(num_points):
            return_values.append(self.get_data_point(name, current_day_index - i))

        return return_values

    def get_column_data(self, name: str) -> list:
        """Gets a column of data from the DataFrame."""
        if type(name) is not str:
            raise Exception('Column name must be a string!')
        return self.__df[name].values.tolist()

    def get_chopped_df(self, window_start_day: int) -> DataFrame:
        """Chops the DataFrame using a start index.

        NOTE: The DataFrame is no longer usable for a simulation once this function is called!
        """
        if type(window_start_day) is not int:
            raise Exception('Window start day must be an integer!')

        self.__df.drop(index=range(0, window_start_day), inplace=True)
        self.__df.reset_index(inplace=True)
        return self.__df

    def __add_candle_colors(self):
        """Adds the candle colors to the DataFrame."""
        open_values = self.get_column_data(self.OPEN)
        close_values = self.get_column_data(self.CLOSE)

        if len(open_values) != len(close_values):
            raise Exception('Data list lengths must match!')

        color_values = []
        for i in range(len(open_values)):
            if float(close_values[i]) > float(open_values[i]):
                color_values.append('green')
            else:
                color_values.append('red')

        self.add_column(self.COLOR, color_values)
