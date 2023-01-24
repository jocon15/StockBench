class DataAPI:
    """"""
    def __init__(self, data):
        self.__df = data

        # constants (public so outside can use them)
        self.CLOSE = 'Close'
        self.OPEN = 'Open'
        self.HIGH = 'High'
        self.LOW = 'Low'

    def add_column(self, name: str, data: any):
        """Adds a list of data as a column in the DataFrame."""
        if type(name) != str:
            raise Exception('Input data type must be a string!')
        if type(data) != list:
            raise Exception('Input data type must be a string!')
        # FIXME: Make sure that a column with that name does not already exist

        self.__df[name] = data

    def get_data_length(self) -> int:
        """Get the length of the DataFrame."""
        return len(self.__df[self.CLOSE])

    def get_column_names(self) -> list:
        """Get the names of the columns in the DataFrame."""
        col_names = list()
        for (col_name, col_vals) in self.__df.iteritems():
            col_names.append(col_name)
        return col_names

    def get_data_point(self, name: str, current_day_index: int):
        """Gets a single data point from the DataFrame."""
        if type(name) != str:
            raise Exception('Input name type must be a string!')
        if type(current_day_index) != int:
            raise Exception('Input day index must be an integer!')

        # The return is type agnostic, as the outside could request data from a column
        # of any type, it's best for the outside to do they type checking themselves.
        # Not ideal but it keeps the number of functions to get data to a minimum.
        # Also, the "outside" is just going to be the simulator.
        return self.__df[name][current_day_index]

    def get_multiple_data_points(self, name: str, current_day_index: int, num_points: int):
        """Gets multiple data points from the DataFrame"""
        return_values = list()
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
