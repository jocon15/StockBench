from StockBench.indicators.indicators import Indicators


class DataAPI:
    """"""
    def __init__(self, data):
        self.__df = data

        # constants (public so outside can use them)
        self.CLOSE = 'Close'
        self.OPEN = 'Open'
        self.HIGH = 'High'
        self.LOW = 'Low'
        self.VOLUME = 'volume'
        self.COLOR = 'color'

    def add_column(self, name: str, data: any):
        """Adds a list of data as a column in the DataFrame."""
        if type(name) != str:
            raise Exception('Input data type must be a string!')
        if type(data) != list:
            raise Exception('Input data type must be a string!')
        for col_name in self.get_column_names():
            if name == col_name:
                raise Exception('A column with that name already exists!')

        self.__df[name] = data

    def get_data_length(self) -> int:
        """Get the length of the DataFrame."""
        return len(self.__df[self.CLOSE])

    def get_column_names(self) -> list:
        """Get the names of the columns in the DataFrame."""
        col_names = list()
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
    
    def add_rsi(self, length: int):
        """Pre-calculate the RSI values and add them to the df.

        Args:
            length (int): The length of the RSI to use.
        """
        # if we already have RSI upper values in the df, we don't need to add them again
        for col_name in self.get_column_names():
            if 'RSI' in col_name:
                return

        # get a list of price values as a list
        price_data = self.get_column_data(self.CLOSE)

        # calculate the RSI values from the indicator API
        rsi_values = Indicators.RSI(length, price_data)

        # add the calculated values to the df
        self.add_column('RSI', rsi_values)

    def add_upper_rsi(self, trigger_value: float):
        """Add upper RSI trigger to the df.

        Args:
            trigger_value (float): The trigger value for the upper RSI.
        """
        # if we already have RSI upper values in the df, we don't need to add them again
        for col_name in self.get_column_names():
            if 'rsi_upper' in col_name:
                return

        # create a list of the trigger value repeated
        list_values = [trigger_value for _ in range(self.get_data_length())]

        # add the list to the data
        self.add_column('RSI_upper', list_values)

    def add_lower_rsi(self, trigger_value: float):
        """Add lower RSI trigger to the df.

        Args:
            trigger_value (float): The trigger value for the lower RSI.
        """
        # if we already have RSI lower values in the df, we don't need to add them again
        for col_name in self.get_column_names():
            if 'rsi_upper' in col_name:
                return

        # create a list of the trigger value repeated
        list_values = [trigger_value for _ in range(self.get_data_length())]

        # add the list to the data
        self.add_column('RSI_lower', list_values)

    def add_stochastic_oscillator(self, length: int):
        """Pre-calculate the RSI values and add them to the df.

        Args:
            length (int): The length of the RSI to use.
        """
        # if we already have SO values in the df, we don't need to add them again
        for col_name in self.get_column_names():
            if 'stochastic_oscillator' in col_name:
                return

        # get data to calculate SO
        high_data = self.get_column_data(self.HIGH)
        low_data = self.get_column_data(self.LOW)
        close_data = self.get_column_data(self.CLOSE)

        # calculate SO
        stochastic_values = Indicators.stochastic_oscillator(length, high_data, low_data, close_data)

        # add the calculated values to the df
        self.add_column('stochastic_oscillator', stochastic_values)

    def add_upper_stochastic(self, trigger_value):
        """Add upper stochastic trigger to the df.

        Args:
            trigger_value (float): The trigger value for the upper stochastic.
        """
        # if we already have values in the df, we don't need to add them again
        for col_name in self.get_column_names():
            if 'stochastic_upper' in col_name:
                return

        # create a list of the trigger value repeated
        list_values = [trigger_value for _ in range(self.get_data_length())]

        # add the list to the data
        self.add_column('stochastic_upper', list_values)

    def add_lower_stochastic(self, trigger_value):
        """Add lower stochastic trigger to the df.

        Args:
            trigger_value (float): The trigger value for the lower stochastic.
        """
        # if we already have values in the df, we don't need to add them again
        for col_name in self.get_column_names():
            if 'stochastic_lower' in col_name:
                return

        # create a list of the trigger value repeated
        list_values = [trigger_value for _ in range(self.get_data_length())]

        # add the list to the data
        self.add_column('stochastic_lower', list_values)

    def add_sma(self, length: int):
        """Pre-calculate the SMA values and add them to the df.

        Args:
            length (int): The length of the SMA to use.
        """
        # get a list of close price values
        column_title = f'SMA{length}'

        # if we already have SMA values in the df, we don't need to add them again
        for col_name in self.get_column_names():
            if column_title in col_name:
                return

        # get a list of price values as a list
        price_data = self.get_column_data(self.CLOSE)

        # calculate the SMA values from the indicator API
        sma_values = Indicators.SMA(length, price_data)

        # add the calculated values to the df
        self.add_column(column_title, sma_values)

    def add_candle_colors(self):
        """Adds the candle colors to the DataFrame."""
        # if we already have SMA values in the df, we don't need to add them again
        for col_name in self.get_column_names():
            if 'Color' in col_name:
                return

        # get the 2 data lists
        open_values = self.get_column_data(self.OPEN)
        close_values = self.get_column_data(self.CLOSE)

        # calculate the colors
        color_values = Indicators.candle_color(open_values, close_values)

        # add the colors to the df
        self.add_column('color', color_values)
