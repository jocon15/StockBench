import os
import re
import sys
import time
from time import perf_counter
import math
import logging
from .constants import *
from datetime import datetime
from .broker.broker_api import BrokerAPI
from .charting.charting_api import ChartingAPI
from .accounting.user_account import UserAccount
from .exporting.exporting_api import ExportingAPI
from .indicators.indicators_api import Indicators
from .position.position_obj import Position
from .triggers.triggering_api import TriggerAPI
from .simulation_data.data_api import DataAPI
from .analysis.analysis_api import SimulationAnalyzer

log = logging.getLogger()


class Simulator:
    """This class defines a simulator object.

    This class serves as the one and only API between the user and the simulation. The simulator handles
    simulation setup and eventual run.


    Here's the breakdown of the simulation data compared to the simulation window:

    ------------ - Additional days needed for accurate indicators at simulation start (algorithm defined)
    |   OHLC   |
    |   OHLC   |
    ------------ - Start of the simulation (user defined)
    |   OHLC   |
    |   OHLC   |
    |   OHLC   |
    |   OHLC   |
    |   OHLC   |
    |   OHLC   |
    ------------ - End of the simulation (user defined)
    """

    def __init__(self, balance: float):
        """Constructor.

        Args:
            balance (float): The initial balance for the account.
        """
        self.__account = UserAccount(balance)
        self.__broker_API = BrokerAPI()
        self.__charting_API = ChartingAPI()
        self.__indicators_API = Indicators()
        self.__exporting_API = ExportingAPI()
        self.__data_API = None  # gets constructed once we request the data
        self.__trigger_API = None  # gets constructed once we have the strategy
        self.__analyzer_API = None  # gets constructed once we have the completed simulation data

        self.__strategy = None
        self.__start_date_unix = None
        self.__end_date_unix = None
        self.__augmented_start_date_unix = None

        self.__symbol = None

        self.__buy_list = list()
        self.__sell_list = list()

        self.__position_archive = list()

        self.__reporting_on = False
        self.__charting_on = False
        self.__user_terminal_logging_on = False

        self.__elapsed_time = None

    def enable_logging(self, terminal=False):
        """Enable user logging.

        Args:
            terminal (bool): Flag for enabling terminal logging in addition to file logging.
        """
        # set the logging level to info
        log.setLevel(logging.INFO)

        # build the filepath
        user_logging_filepath = os.path.join('logs', f'RunLog_{self.__datetime_nonce_string()}')

        # build the formatters
        user_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')

        # make the directories if they don't already exist
        os.makedirs(os.path.dirname(user_logging_filepath), exist_ok=True)

        # create the handler
        user_handler = logging.FileHandler(user_logging_filepath)

        # set the format of the handler
        user_handler.setFormatter(user_logging_formatter)

        # add the handler to the logger
        log.addHandler(user_handler)

        if terminal:
            # create the terminal handler
            terminal_handler = logging.StreamHandler(sys.stdout)

            # set the formal of the handler
            terminal_handler.setFormatter(user_logging_formatter)

            # add the handler to the logger
            log.addHandler(terminal_handler)

            # tell the developer logging that we're using the terminal
            self.__user_terminal_logging_on = True

    def enable_developer_logging(self, level=2, terminal=False):
        """Enable developer logging.

        Args:
            level (int): The logging level for the logger.
            terminal (bool): Flag for enabling terminal logging in addition to file logging.

        Notes:
            - If user_logging terminal is enabled, it will supersede the developer terminal logging.
                Make sure the user terminal logging is disabled before enabling developer terminal logging.
        """
        # set the logging level
        if level == 1:
            log.setLevel(logging.DEBUG)
            # build the formatter
            developer_logging_formatter = logging.Formatter('%(funcName)s:%(lineno)d|%(levelname)s|%(message)s')
        elif level == 3:
            log.setLevel(logging.WARNING)
            # build the formatter
            developer_logging_formatter = logging.Formatter('%(lineno)d|%(levelname)s|%(message)s')
        elif level == 4:
            log.setLevel(logging.ERROR)
            # build the formatter
            developer_logging_formatter = logging.Formatter('%(lineno)d|%(levelname)s|%(message)s')
        elif level == 5:
            log.setLevel(logging.CRITICAL)
            # build the formatter
            developer_logging_formatter = logging.Formatter('%(lineno)d|%(levelname)s|%(message)s')
        else:
            log.setLevel(logging.INFO)
            # build the formatter
            developer_logging_formatter = logging.Formatter('%(lineno)d|%(levelname)s|%(message)s')

        # build the filepath
        developer_logging_filepath = os.path.join('dev', f'DevLog_{self.__datetime_nonce_string()}')

        # make the directories if they don't already exist
        os.makedirs(os.path.dirname(developer_logging_filepath), exist_ok=True)

        # create the handler
        developer_handler = logging.FileHandler(developer_logging_filepath)

        # set the format of the handler
        developer_handler.setFormatter(developer_logging_formatter)

        # add the handler to the logger
        log.addHandler(developer_handler)

        if terminal:
            if not self.__user_terminal_logging_on:
                # create the terminal handler
                terminal_handler = logging.StreamHandler(sys.stdout)

                # set the formal of the handler
                terminal_handler.setFormatter(developer_logging_formatter)

                # add the handler to the logger
                log.addHandler(terminal_handler)

    def enable_reporting(self):
        """Enable report building."""
        self.__reporting_on = True

    def enable_charting(self):
        """Enable charting."""
        self.__charting_on = True

    def load_strategy(self, strategy: dict):
        """Load a strategy.

         Args:
             strategy (dict): The strategy as a dictionary.
         """
        # initialize the member variable
        self.__strategy = strategy
        # initialize the member object
        self.__trigger_API = TriggerAPI(strategy)

    def run(self, symbol: str) -> dict:
        """Run a simulation on an asset.

        Args:
            symbol (str): The symbol to run the simulation on.
        """
        # set the objects symbol to the passed value, so we can use it everywhere
        log.info(f'Setting up simulation for symbol: {symbol}...')
        start_time = perf_counter()
        self.__symbol = symbol.upper()

        # check the strategy for errors
        self.__error_check_strategy()

        # parse the strategy for timestamps, so we know what the user wants
        self.__parse_strategy_timestamps()

        # get the data from the servers
        temp_df = self.__broker_API.get_daily_data(self.__symbol,
                                                   self.__augmented_start_date_unix,
                                                   self.__end_date_unix)

        # initialize the data api with the broker data
        self.__data_API = DataAPI(temp_df)

        # parse the strategy for rules
        self.__parse_strategy_rules()

        # calculate window lengths
        total_days = int((self.__end_date_unix - self.__augmented_start_date_unix) / SECONDS_1_DAY)
        days_in_focus = int((self.__end_date_unix - self.__start_date_unix) / SECONDS_1_DAY)
        sim_window_start_day = total_days - days_in_focus
        trade_able_days = self.__data_API.get_data_length() - sim_window_start_day

        # initialize the lists to the correct size (values to None)
        self.__buy_list = [None for _ in range(self.__data_API.get_data_length())]
        self.__sell_list = [None for _ in range(self.__data_API.get_data_length())]

        log.info(f'Setup for symbol: {self.__symbol} complete')

        log.info('==== Simulation Details =====')
        log.info(f'Symbol          : {self.__symbol}')
        log.info(f'Start Date      : {self.__unix_to_string(self.__start_date_unix)}')
        log.info(f'End Date        : {self.__unix_to_string(self.__end_date_unix)}')
        log.info(f'Window Size     : {days_in_focus}')
        log.info(f'Trade-able Days : {trade_able_days}')
        log.info(f'Account Value   : {self.__account.get_balance()}')
        log.info('=============================')

        buy_mode = True
        position = None

        log.info(f'Beginning simulation...')

        # ===================== Simulation Loop ======================
        for current_day_index in range(sim_window_start_day, self.__data_API.get_data_length()):
            # we loop from the focus start day (ex. 200)
            # to the total amount of days in the set (ex. 400)
            # the day_index represents the index of the current day in the
            # data set, so if we need something like SMA200 we just get all
            # the days from now to now-200
            # we can have an indicator package like viper that takes a df
            # a start and an end day and calculate the SMA X

            log.debug(f'Current day index: {current_day_index}')

            if buy_mode:
                was_triggered = self.__trigger_API.check_buy_triggers(self.__data_API, current_day_index)
                if was_triggered:
                    # create a position
                    position = self.__create_position(current_day_index)
                    # switch to selling
                    buy_mode = False
            else:
                # sell mode
                was_triggered = self.__trigger_API.check_sell_triggers(self.__data_API, position, current_day_index)
                if was_triggered:
                    # close the position
                    self.__liquidate_position(position, current_day_index)
                    # clear the stored position
                    position = None
                    # switch to buying
                    buy_mode = True
                elif current_day_index == (self.__data_API.get_data_length() - 1):
                    # the position is still open at the end of the simulation
                    log.info('Position closed due to end of simulation reached')
                    # check that position still exists - if so sell
                    if position:
                        # close the position
                        self.__liquidate_position(position, current_day_index)
                    # exit the loop as a precaution
                    break

        # add the buys and sells to the df
        self.__add_buys_sells()

        # get the chopped DataFrame
        chopped_temp_df = self.__data_API.get_chopped_df(sim_window_start_day)

        log.info('Simulation complete!')

        # initiate the analyzer with the positions data
        self.__analyzer_API = SimulationAnalyzer(self.__position_archive)

        end_time = perf_counter()
        self.__elapsed_time = end_time - start_time

        log.info('====== Simulation Results ======')
        log.info(f'Elapsed time  : {self.__elapsed_time} seconds')
        log.info(f'Trades made   : {len(self.__position_archive)}')
        log.info(f'Effectiveness : {self.__analyzer_API.effectiveness()}')
        log.info(f'Avg. P/L      : {self.__analyzer_API.avg_profit_loss()}')
        log.info(f'Total P/L     : {self.__account.get_profit_loss()}')
        log.info(f'Account Value : {self.__account.get_balance()}')
        log.info('================================')

        self.__print_results()

        if self.__reporting_on:
            # load exporter with the chopped data
            self.__exporting_API.load_data(chopped_temp_df)
            # export the data
            self.__exporting_API.export()

        if self.__charting_on:
            # chart the chopped data
            self.__charting_API.chart(chopped_temp_df, self.__symbol)

        return {
            'symbol': symbol,
            'trades_made': len(self.__position_archive),
            'effectiveness': self.__analyzer_API.effectiveness(),
            'average_profit_loss': self.__analyzer_API.avg_profit_loss(),
            'total_profit_loss': self.__account.get_profit_loss(),
            'account_value': self.__account.get_balance()
        }

    def run_multiple(self, symbols: list) -> list:
        results = list()
        for symbol in symbols:
            results.append(self.run(symbol))

        return results

    def __error_check_strategy(self):
        """Check the strategy for errors"""
        log.debug('Checking strategy for errors...')
        if not self.__strategy:
            log.critical('No strategy uploaded')
            raise Exception('No strategy uploaded')
        if 'start' not in self.__strategy.keys():
            log.critical("Strategy missing 'start' key")
            raise Exception("Strategy missing 'start' key")
        if 'end' not in self.__strategy.keys():
            log.critical("Strategy missing 'end' key")
            raise Exception("Strategy missing 'end' key")
        if 'buy' not in self.__strategy.keys():
            log.critical("Strategy missing 'buy' key")
            raise Exception("Strategy missing 'buy' key")
        if 'sell' not in self.__strategy.keys():
            log.critical("Strategy missing 'sell' key")
            raise Exception("Strategy missing 'sell' key")
        log.debug('No errors found in the strategy')

    def __parse_strategy_timestamps(self):
        """Parse the strategy for relevant information needed to make the API request."""
        log.debug('Parsing strategy for timestamps...')
        if 'start' in self.__strategy.keys():
            self.__start_date_unix = int(self.__strategy['start'])
        if 'end' in self.__strategy.keys():
            self.__end_date_unix = int(self.__strategy['end'])

        additional_days = 0

        # build a list of sub keys from the buy and sell sections
        keys = list()
        if 'buy' in self.__strategy.keys():
            for key in self.__strategy['buy'].keys():
                keys.append(key)
        if 'sell' in self.__strategy.keys():
            for key in self.__strategy['sell'].keys():
                keys.append(key)

        for key in keys:
            if 'RSI' in key:
                # ======== key based =========
                nums = re.findall(r'\d+', key)
                if len(nums) == 1:
                    num = int(nums[0])
                    if additional_days < num:
                        additional_days = num
                    # add the RSI data to the df
                    self.__add_rsi(num)
                else:
                    additional_days = DEFAULT_RSI_LENGTH
            elif 'SMA' in key:
                nums = re.findall(r'\d+', key)
                if len(nums) == 1:
                    num = int(nums[0])
                    if additional_days < num:
                        additional_days = num
            elif 'color' in key:
                try:
                    num = len(self.__strategy['buy']['color'])
                    if type(self.__strategy['buy']['color']) != dict:
                        raise Exception('Candle stick signals must be a dict')
                except KeyError:
                    num = len(self.__strategy['sell']['color'])
                if additional_days < num:
                    additional_days = num

        # add a buffer
        if additional_days != 0:
            # we figure 2 weekdays and a holiday for every week of additional days
            # since it gets cast to int, the decimal is cut off -> it's usually < 3 per week after cast
            additional_days += int((additional_days / 7) * 3)
        # now, we should always have enough days to supply the indicators that the user requires

        self.__error_check_timestamps(self.__start_date_unix, self.__end_date_unix)
        self.__augmented_start_date_unix = self.__start_date_unix - (additional_days * SECONDS_1_DAY)

    def __parse_strategy_rules(self):
        """Parse the strategy for relevant information needed to make the API request."""
        log.debug('Parsing strategy for indicators and rules...')

        # build a list of sub keys from the buy and sell sections
        keys = list()
        if 'buy' in self.__strategy.keys():
            for key in self.__strategy['buy'].keys():
                keys.append(key)
        if 'sell' in self.__strategy.keys():
            for key in self.__strategy['sell'].keys():
                keys.append(key)

        def rsi_buy(_key, _value):
            # ======== key based =========
            nums = re.findall(r'\d+', _key)
            if len(nums) == 1:
                num = int(nums[0])
                # add the RSI data to the df
                self.__add_rsi(num)
            else:
                # add the RSI data to the df
                self.__add_rsi(DEFAULT_RSI_LENGTH)
            # ======== value based (rsi limit)=========
            # _value = self.__strategy['buy'][key]
            _nums = re.findall(r'\d+', _value)
            if len(_nums) == 1:
                _trigger = float(_nums[0])
                self.__add_lower_rsi(_trigger)

        def sma_buy(_key):
            nums = re.findall(r'\d+', _key)
            if len(nums) == 1:
                num = int(nums[0])
                # add the SMA data to the df
                self.__add_sma(num)

        def rsi_sell(_key, _value):
            # ======== key based =========
            nums = re.findall(r'\d+', _key)
            if len(nums) == 1:
                num = int(nums[0])
                # add the RSI data to the df
                self.__add_rsi(num)
            else:
                # add the RSI data to the df
                self.__add_rsi(DEFAULT_RSI_LENGTH)
            # ======== value based (rsi limit)=========
            # _value = self.__strategy['sell'][key]
            _nums = re.findall(r'\d+', _value)
            if len(_nums) == 1:
                _trigger = float(_nums[0])
                self.__add_upper_rsi(_trigger)

        def sma_sell(_key):
            nums = re.findall(r'\d+', _key)
            if len(nums) == 1:
                num = int(nums[0])
                # add the SMA data to the df
                self.__add_sma(num)

        # buy keys
        for key in self.__strategy['buy'].keys():
            if 'RSI' in key:
                rsi_buy(key, self.__strategy['buy'][key])
            elif 'SMA' in key:
                sma_buy(key)
            elif 'color' in key:
                self.__add_candle_colors()
            elif 'and' in key:
                for inner_key in self.__strategy['buy'][key].keys():
                    if 'RSI' in inner_key:
                        rsi_buy(inner_key, self.__strategy['buy'][key][inner_key])
                    elif 'SMA' in inner_key:
                        sma_buy(inner_key)

        # sell keys
        for key in self.__strategy['sell'].keys():
            if 'RSI' in key:
                rsi_sell(key, self.__strategy['sell'][key])
            elif 'SMA' in key:
                sma_sell(key)
            elif 'color' in key:
                self.__add_candle_colors()
            elif 'and' in key:
                for inner_key in self.__strategy['sell'][key].keys():
                    if 'RSI' in inner_key:
                        rsi_sell(inner_key, self.__strategy['sell'][key][inner_key])
                    elif 'SMA' in inner_key:
                        sma_sell(inner_key)

    def __add_rsi(self, length: int):
        """Pre-calculate the RSI values and add them to the df.

        Args:
            length (int): The length of the RSI to use.
        """
        # if we already have RSI upper values in the df, we don't need to add them again
        for col_name in self.__data_API.get_column_names():
            if 'RSI' in col_name:
                return

        # get a list of price values as a list
        price_data = self.__data_API.get_column_data(self.__data_API.CLOSE)

        # calculate the RSI values from the indicator API
        rsi_values = self.__indicators_API.RSI(length, price_data)

        # add the calculated values to the df
        self.__data_API.add_column('RSI', rsi_values)

    def __add_upper_rsi(self, trigger_value: float):
        """Add upper RSI trigger to the df.

        Args:
            trigger_value (float): The trigger value for the upper RSI.
        """
        # if we already have RSI upper values in the df, we don't need to add them again
        for col_name in self.__data_API.get_column_names():
            if 'rsi_upper' in col_name:
                return

        # create a list of the trigger value repeated
        list_values = [trigger_value for _ in range(self.__data_API.get_data_length())]

        # add the list to the data
        self.__data_API.add_column('RSI_upper', list_values)

    def __add_lower_rsi(self, trigger_value: float):
        """Add lower RSI trigger to the df.

        Args:
            trigger_value (float): The trigger value for the lower RSI.
        """
        # if we already have RSI lower values in the df, we don't need to add them again
        for col_name in self.__data_API.get_column_names():
            if 'rsi_upper' in col_name:
                return

        # create a list of the trigger value repeated
        list_values = [trigger_value for _ in range(self.__data_API.get_data_length())]

        # add the list to the data
        self.__data_API.add_column('RSI_lower', list_values)

    def __add_sma(self, length: int):
        """Pre-calculate the SMA values and add them to the df.

        Args:
            length (int): The length of the SMA to use.
        """
        # get a list of close price values
        column_title = f'SMA{length}'

        # if we already have SMA values in the df, we don't need to add them again
        for col_name in self.__data_API.get_column_names():
            if column_title in col_name:
                return

        # get a list of price values as a list
        price_data = self.__data_API.get_column_data(self.__data_API.CLOSE)

        # calculate the SMA values from the indicator API
        sma_values = self.__indicators_API.SMA(length, price_data)

        # add the calculated values to the df
        self.__data_API.add_column(column_title, sma_values)

    def __add_buys_sells(self):
        """Adds the buy and sell lists to the DataFrame."""
        self.__data_API.add_column('Buy', self.__buy_list)
        self.__data_API.add_column('Sell', self.__sell_list)

    def __add_candle_colors(self):
        """Adds the candle colors to the DataFrame."""
        # if we already have SMA values in the df, we don't need to add them again
        for col_name in self.__data_API.get_column_names():
            if 'Color' in col_name:
                return

        # get the 2 data lists
        open_values = self.__data_API.get_column_data(self.__data_API.OPEN)
        close_values = self.__data_API.get_column_data(self.__data_API.CLOSE)

        # calculate the colors
        color_values = self.__indicators_API.candle_color(open_values, close_values)

        # add the colors to the df
        self.__data_API.add_column('color', color_values)

    def __create_position(self, current_day_index: int) -> Position:
        """Creates a position and updates the account.

        Args:
            current_day_index (int): The index of the current day

        return:
            Position: The created Position object.

        Notes:
            The assumption is that the user wants to use full buying power (for now)
        """
        log.info('Creating the position...')

        # add the buying price to the DataFrame
        _buy_price = self.__data_API.get_data_point(self.__data_API.CLOSE, current_day_index)

        # calculate the withdrawal amount (nearest whole share - floor direction)
        share_count = float(math.floor(self.__account.get_balance() / _buy_price))
        withdraw_amount = round(_buy_price * share_count, 3)

        # withdraw the money from the account
        self.__account.withdraw(withdraw_amount)

        # Adding the buy price to the buy list
        self.__buy_list[current_day_index] = _buy_price

        log.info('Position created successfully')

        # build and return the new position
        return Position(_buy_price, share_count)

    def __liquidate_position(self, position: Position, current_day_index: int):
        """Closes the position and updates the account.

        Args:
            position (Position): The position to close.
            current_day_index (int): The index of the current day
        """
        log.info('Closing the position...')

        # get the cosing price
        _sell_price = float(self.__data_API.get_data_point(self.__data_API.CLOSE, current_day_index))

        # close the position
        position.close_position(_sell_price)

        # add the position to the archive
        self.__position_archive.append(position)

        # calculate the deposit amount
        deposit_amount = round(_sell_price * position.get_share_count(), 3)

        log.info('Position closed successfully')

        # deposit the value of the position to the account
        self.__account.deposit(deposit_amount)

        # Adding the sell price to the sell list
        self.__sell_list[current_day_index] = _sell_price

    def __print_results(self):
        """Prints the simulation results if terminal logging is off"""
        if not self.__user_terminal_logging_on:
            print('====== Simulation Results ======')
            print(f'Elapsed time  : {self.__elapsed_time} seconds')
            print(f'Trades made   : {len(self.__position_archive)}')
            print(f'Effectiveness : {self.__analyzer_API.effectiveness()}%')
            print(f'Avg. P/L      : ${self.__analyzer_API.avg_profit_loss()}')
            print(f'Total P/L     : ${self.__account.get_profit_loss()}')
            print(f'Account Value : ${self.__account.get_balance()}')
            print('================================')

    @staticmethod
    def __datetime_nonce_string() -> str:
        """Convert current date and time to string."""
        return datetime.now().strftime("%m_%d_%Y__%H_%M_%S")

    @staticmethod
    def __unix_to_string(_unix_date, _format='%m-%d-%Y') -> str:
        """Convert a unix date to a string of custom format.

        Args:
            _unix_date (int): The unix timestamp to convert.
            _format (str): The format to convert to.

        return:
            str: The converted string in custom format.
        """
        return datetime.utcfromtimestamp(_unix_date).strftime(_format)

    @staticmethod
    def __error_check_timestamps(start, end):
        """Simple check that the timestamps are valid.

        Args:
            start (any): Unix timestamp of the start date.
            end (any): Unix timestamp of the end date.
        """
        if start > end:
            log.critical('Start timestamp must be before end timestamp')
            raise Exception('Start timestamp must be before end timestamp')
        if start > int(time.time()):
            log.critical('Start timestamp must not be in the future')
            raise Exception('Start timestamp must not be in the future')
