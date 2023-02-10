import os
import re
import json
import time
import math
import logging
from tqdm import tqdm
from .constants import *
from time import perf_counter
from datetime import datetime
from multiprocessing import Process
from .broker.broker_api import BrokerAPI
from .display.singular import SingularDisplay
from .display.multiple import MultipleDisplay
from .accounting.user_account import UserAccount
from .exporting.exporting_api import ExportingAPI
from .position.position_obj import Position
from .triggers.triggering_api import TriggerAPI
from .simulation_data.data_api import DataAPI
from .analysis.analysis_api import SimulationAnalyzer
from .function_tools.nonce import datetime_nonce

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
        self.__running_multiple = False

        self.__elapsed_time = None

        self.__stored_results = None

        # folder paths
        self.__save_folder = 'saved_simulations'
        self.__logs_folder = 'logs'
        self.__dev_folder = 'dev'

    def enable_reporting(self):
        """Enable report building."""
        self.__reporting_on = True

    def load_strategy(self, strategy: dict):
        """Load a strategy.

         Args:
             strategy (dict): The strategy as a dictionary.
         """
        # initialize the member variable
        self.__strategy = strategy
        # initialize the member object
        self.__trigger_API = TriggerAPI(strategy)

    def run(self, symbol: str, show_chart=True, save_chart=False) -> dict:
        """Run a simulation on an asset.

        Args:
            symbol (str): The symbol to run the simulation on.
            show_chart (bool): Show the chart when finished.
            save_chart (bool): Save the chart when finished.
        """
        # set the objects symbol to the passed value, so we can use it everywhere
        log.info(f'Setting up simulation for symbol: {symbol}...')
        start_time = perf_counter()

        self.__symbol = symbol.upper()

        # reset the attributes()
        self.__reset_attributes()

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

        # parse the strategy for rules (adds indicator data to the df)
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

        if not self.__running_multiple:
            self.__print_header()

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

        if not self.__running_multiple:
            self.__print_results()

        if self.__reporting_on:
            # create an exporting object
            exporting_API = ExportingAPI()
            # export the data on a separate process
            exporting_process = Process(target=exporting_API.export, args=(chopped_temp_df, self.__symbol))
            exporting_process.start()

        if show_chart or save_chart:
            # create the display object
            charting_API = SingularDisplay()
            # chart the data on a separate process
            charting_process = Process(target=charting_API.chart,
                                       args=(chopped_temp_df, self.__symbol, show_chart, save_chart))
            charting_process.start()

        return {
            'symbol': self.__symbol,
            'trades_made': len(self.__position_archive),
            'effectiveness': self.__analyzer_API.effectiveness(),
            'average_profit_loss': self.__analyzer_API.avg_profit_loss(),
            'total_profit_loss': self.__account.get_profit_loss(),
            'account_value': self.__account.get_balance()
        }

    def run_multiple(self,
                     symbols: list,
                     show_individual_charts=False,
                     save_individual_charts=False,
                     show_chart=True,
                     save_chart=False) -> list:
        """Simulate a list of assets.

        Args:
            symbols (list): The list of assets to simulation.
            show_individual_charts (bool): Show a chart for each symbol.
            save_individual_charts (bool): Save the chart for each symbol.
            show_chart (bool): Show the chart when finished.
            save_chart (bool): Save the chart when finished.
        """
        # disable printing for TQDM
        self.__running_multiple = True

        # simulate each symbol
        results = list()
        for symbol in tqdm(symbols, f'Simulating {len(symbols)} symbols'):
            try:
                result = self.run(symbol, show_individual_charts, save_individual_charts)
            except Exception as e:
                print(f'\nException {type(e)} caught, retrying...')
                result = self.run(symbol)
            results.append(result)

        # re-enable printing for TQDM
        self.__running_multiple = False
        # save the results in case the user wants to write them to file
        self.__stored_results = results

        # create the display object
        display = MultipleDisplay()
        display.chart(results, show_chart, save_chart)
        return results

    def save_results_json(self, file_name=None):
        """Save results of a multiple simulation to a JSON file.

        Args:
            file_name (str): The desired name of the JSON file.
        """
        # validate file name
        if not file_name:
            log.debug('No filename entered, using nonce')
            file_name = f'save_{datetime_nonce()}'
        else:
            file_name = file_name.replace('.json', '')

        # check for stored results
        if self.__stored_results:
            filepath = os.path.join(self.__save_folder, f'{file_name}.json')
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # write the results to the file
            with open(filepath, 'w') as file:
                json.dump(self.__stored_results, file, indent=4)
        else:
            log.debug('No stored data available to write! Run a multi-sim first using run_multiple()')

    def display_results_from_json(self, file_name: str, save_chart=False):
        """Load and display the results from a JSON file.

        Args:
            file_name (str): The name of the file to load.
            save_chart (bool): Save the chart that was displayed.
        """
        # validate file name
        if file_name == '':
            log.error('Save file name cannot be empty string')
            raise Exception('Save file name cannot be empty string')
        else:
            file_name = file_name.replace('.json', '')

        # build the path of the JSON file
        filepath = os.path.join(self.__save_folder, f'{file_name}.json')

        # make sure that the JSON file actually exists
        if not os.path.exists(filepath):
            log.error('Specified save file does not exist!')
            raise Exception('Specified save file does not exist!')

        # load the data from the file
        with open(filepath, 'r') as file:
            results = json.load(file)

        # display the loaded data
        display = MultipleDisplay()
        display.chart(results, True, save_chart)
        return results

    def enable_logging(self):
        """Enable user logging."""
        # set the logging level to info
        log.setLevel(logging.INFO)

        # build the filepath
        user_logging_filepath = os.path.join(self.__logs_folder, f'RunLog_{datetime_nonce()}')

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

    def enable_developer_logging(self, level=2):
        """Enable developer logging.

        Args:
            level (int): The logging level for the logger.
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
        developer_logging_filepath = os.path.join(self.__dev_folder, f'DevLog_{datetime_nonce()}')

        # make the directories if they don't already exist
        os.makedirs(os.path.dirname(developer_logging_filepath), exist_ok=True)

        # create the handler
        developer_handler = logging.FileHandler(developer_logging_filepath)

        # set the format of the handler
        developer_handler.setFormatter(developer_logging_formatter)

        # add the handler to the logger
        log.addHandler(developer_handler)

    def __reset_attributes(self):
        self.__account.reset()
        self.__buy_list = list()
        self.__sell_list = list()
        self.__position_archive = list()

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
                    self.__data_API.add_rsi(num)
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
                self.__data_API.add_rsi(num)
            else:
                # add the RSI data to the df
                self.__data_API.add_rsi(DEFAULT_RSI_LENGTH)
            # ======== value based (rsi limit)=========
            # _value = self.__strategy['buy'][key]
            _nums = re.findall(r'\d+', _value)
            if len(_nums) == 1:
                _trigger = float(_nums[0])
                self.__data_API.add_lower_rsi(_trigger)

        def sma_buy(_key):
            nums = re.findall(r'\d+', _key)
            if len(nums) == 1:
                num = int(nums[0])
                # add the SMA data to the df
                self.__data_API.add_sma(num)

        def rsi_sell(_key, _value):
            # ======== key based =========
            nums = re.findall(r'\d+', _key)
            if len(nums) == 1:
                num = int(nums[0])
                # add the RSI data to the df
                self.__data_API.add_rsi(num)
            else:
                # add the RSI data to the df
                self.__data_API.add_rsi(DEFAULT_RSI_LENGTH)
            # ======== value based (rsi limit)=========
            # _value = self.__strategy['sell'][key]
            _nums = re.findall(r'\d+', _value)
            if len(_nums) == 1:
                _trigger = float(_nums[0])
                self.__data_API.add_upper_rsi(_trigger)

        def sma_sell(_key):
            nums = re.findall(r'\d+', _key)
            if len(nums) == 1:
                num = int(nums[0])
                # add the SMA data to the df
                self.__data_API.add_sma(num)

        # buy keys
        for key in self.__strategy['buy'].keys():
            if 'RSI' in key:
                rsi_buy(key, self.__strategy['buy'][key])
            elif 'SMA' in key:
                sma_buy(key)
            elif 'color' in key:
                self.__data_API.add_candle_colors()
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
                self.__data_API.add_candle_colors()
            elif 'and' in key:
                for inner_key in self.__strategy['sell'][key].keys():
                    if 'RSI' in inner_key:
                        rsi_sell(inner_key, self.__strategy['sell'][key][inner_key])
                    elif 'SMA' in inner_key:
                        sma_sell(inner_key)

    def __add_buys_sells(self):
        """Adds the buy and sell lists to the DataFrame."""
        self.__data_API.add_column('Buy', self.__buy_list)
        self.__data_API.add_column('Sell', self.__sell_list)

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

    def __print_header(self):
        """Prints the simulation header."""
        print('======= Simulation Start =======')
        print(f'Running simulation on {self.__symbol}...')
        print('================================')

    def __print_results(self):
        """Prints the simulation results."""
        print('====== Simulation Results ======')
        print(f'Elapsed time  : {self.__elapsed_time} seconds')
        print(f'Trades made   : {len(self.__position_archive)}')
        print(f'Effectiveness : {self.__analyzer_API.effectiveness()}%')
        print(f'Avg. P/L      : ${self.__analyzer_API.avg_profit_loss()}')
        print(f'Total P/L     : ${self.__account.get_profit_loss()}')
        print(f'Account Value : ${self.__account.get_balance()}')
        print('================================')

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
