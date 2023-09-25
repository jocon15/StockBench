class DataManager:
    """"""
    def __init__(self, data):
        # constants (public so outside can use them)
        self.CLOSE = 'Close'
        self.OPEN = 'Open'
        self.HIGH = 'High'
        self.LOW = 'Low'
        self.VOLUME = 'volume'
        self.COLOR = 'color'

        self.__df = data
        # add candle colors to the data
        self.__add_candle_colors()

    def add_column(self, name: str, data: any):
        """Adds a list of data as a column in the DataFrame."""
        if type(name) != str:
            raise Exception('Input data type must be a string!')
        if type(data) != list:
            raise Exception('Input data type must be a string!')
        for col_name in self.get_column_names():
            if name == col_name:
                # a column with that name already exists, skip
                return

        self.__df[name] = data

    def get_data_length(self) -> int:
        """Get the length of the DataFrame."""
        return len(self.__df[self.CLOSE])

    def get_column_names(self) -> list:
        """Get the names of the columns in the DataFrame."""
        col_names = []
        for (col_name, col_vals) in self.__df.items():
            col_names.append(col_name)
        return col_names

    def get_data_point(self, column_name: str, current_day_index: int):
        """Gets a single data point from the DataFrame."""
        if type(column_name) != str:
            raise Exception('Input name type must be a string!')
        if type(current_day_index) != int:
            raise Exception('Input day index must be an integer!')

        # The return is type agnostic, as the outside could request data from a column
        # of any type, it's best for the outside to do they type checking themselves.
        # Not ideal but it keeps the number of functions to get data to a minimum.
        # Also, the "outside" is just going to be the simulator.
        return self.__df[column_name][current_day_index]

    def get_multiple_data_points(self, name: str, current_day_index: int, num_points: int):
        """Gets multiple data points from the DataFrame"""
        return_values = []
        for i in range(num_points):
            return_values.append(self.get_data_point(name, current_day_index - i))

        return return_values

    def get_column_data(self, name: str):
        """Gets a column of data from the DataFrame."""
        if type(name) != str:
            raise Exception('Input name type must be a string!')
        # FIXME: check that the column is actually in the dataframe
        return self.__df[name].values.tolist()

    def get_chopped_df(self, window_start_day: int):
        """chop the dataframe and reset index

        NOTE: The df is no longer usable for a simulation once this function is called!
        """
        if type(window_start_day) != int:
            raise Exception('Input window start day must be an integer!')

        self.__df.drop(index=range(0, window_start_day), inplace=True)
        self.__df.reset_index(inplace=True)
        return self.__df

    def __add_candle_colors(self):
        """Adds the candle colors to the DataFrame."""

        # get the 2 data lists
        open_values = self.get_column_data(self.OPEN)
        close_values = self.get_column_data(self.CLOSE)

        # calculate the colors
        if len(open_values) != len(close_values):
            raise Exception('Data list lengths must match!')

        color_values = []
        for i in range(len(open_values)):
            if float(close_values[i]) > float(open_values[i]):
                color_values.append('green')
            else:
                color_values.append('red')

        # add the colors to the df
        self.add_column('color', color_values)
