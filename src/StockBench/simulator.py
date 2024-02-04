import os
import time
import math
import logging
from tqdm import tqdm
from .constants import *
from time import perf_counter
from datetime import datetime
from .broker.broker import Broker
from .export.export import Exporter
from .position.position import Position
from .display.display import Display
from .display.singular import SingularDisplay
from .display.multiple import MultipleDisplay
from .simulation_data.data_manager import DataManager
from .account.user_account import UserAccount
from .function_tools.nonce import datetime_nonce
from .indicator.indicator_manager import IndicatorManager
from .analysis.analyzer import SimulationAnalyzer
from .triggers.trigger_manager import TriggerManager

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
        self.__broker = Broker()
        self.__data_manager = None  # gets constructed once we request the data
        self.__trigger_manager = None  # gets constructed once we have the strategy

        self.__strategy = None
        self.__start_date_unix = None
        self.__end_date_unix = None
        self.__augmented_start_date_unix = None

        self.__symbol = None

        self.__buy_list = []
        self.__sell_list = []

        self.__single_simulation_position_archive = []
        self.__multiple_simulation_position_archive = []

        self.__reporting_on = False
        self.__running_multiple = False

        self.__indicators = IndicatorManager.load_indicators()

        self.__stored_results = None

        # folder paths
        self.__save_folder = 'saved_simulations'
        self.__logs_folder = 'logs'
        self.__dev_folder = 'dev'

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
            developer_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')
        elif level == 4:
            log.setLevel(logging.ERROR)
            # build the formatter
            developer_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')
        elif level == 5:
            log.setLevel(logging.CRITICAL)
            # build the formatter
            developer_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')
        else:
            log.setLevel(logging.INFO)
            # build the formatter
            developer_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')

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
        self.__trigger_manager = TriggerManager(strategy, self.__indicators.values())

    def run(self, symbol: str, show_chart=True, save_option=Display.TEMP_SAVE, progress_observer=None) -> dict:
        """Run a simulation on an asset.

        Args:
            symbol (str): The symbol to run the simulation on.
            show_chart (bool): Show the chart when finished.
            save_option (int): Save the chart when finished.
            progress_observer (any): Observer object to update progress to.
        """
        # set the objects symbol to the passed value, so we can use it everywhere
        log.info(f'Setting up simulation for symbol: {symbol}...')
        start_time = perf_counter()

        self.__symbol = symbol.upper()

        # reset the attributes()
        self.__reset_singular_attributes()

        # check the strategy for errors
        self.__error_check_strategy()

        # parse the strategy for timestamps, so we know what the user wants
        self.__parse_strategy_timestamps()

        # get the data from the servers
        temp_df = self.__broker.get_daily_data(self.__symbol,
                                               self.__augmented_start_date_unix,
                                               self.__end_date_unix)

        # initialize the data api with the broker data
        self.__data_manager = DataManager(temp_df)

        # parse the strategy for rules (adds indicator data to the df)
        self.__parse_strategy_rules()

        # calculate window lengths
        total_days = int((self.__end_date_unix - self.__augmented_start_date_unix) / SECONDS_1_DAY)
        days_in_focus = int((self.__end_date_unix - self.__start_date_unix) / SECONDS_1_DAY)
        sim_window_start_day = total_days - days_in_focus
        trade_able_days = self.__data_manager.get_data_length() - sim_window_start_day

        # initialize the lists to the correct size (values to None)
        self.__buy_list = [None for _ in range(self.__data_manager.get_data_length())]
        self.__sell_list = [None for _ in range(self.__data_manager.get_data_length())]

        log.info(f'Setup for symbol: {self.__symbol} complete')

        self.__log_details(self.__symbol, self.__unix_to_string(self.__start_date_unix),
                           self.__unix_to_string(self.__end_date_unix), days_in_focus, trade_able_days,
                           self.__account.get_balance())

        if not self.__running_multiple:
            self.__print_header()

        buy_mode = True
        position = None

        log.info(f'Beginning simulation...')

        # calculate the increment for the progress bar
        increment = 1.0  # must supply default value
        if progress_observer is not None:
            increment = 100.0 / (self.__data_manager.get_data_length() - sim_window_start_day)

        # ===================== Simulation Loop ======================
        for current_day_index in range(sim_window_start_day, self.__data_manager.get_data_length()):
            # Loop from the focus start day (ex. 200) to the total amount of days in the set (ex. 400).
            # The day_index represents the index of the current day in the data set.

            log.debug(f'Current day index: {current_day_index}')

            if buy_mode:
                was_triggered = self.__trigger_manager.check_buy_triggers(self.__data_manager, current_day_index)
                if was_triggered:
                    # create a position
                    position = self.__create_position(current_day_index)
                    # switch to selling
                    buy_mode = False
            else:
                # sell mode
                was_triggered = self.__trigger_manager.check_sell_triggers(self.__data_manager, position,
                                                                           current_day_index)
                if was_triggered:
                    # close the position
                    self.__liquidate_position(position, current_day_index)
                    # clear the stored position
                    position = None
                    # switch to buying
                    buy_mode = True
                elif current_day_index == (self.__data_manager.get_data_length() - 1):
                    # the position is still open at the end of the simulation
                    log.info('Position closed due to end of simulation reached')
                    # check that position still exists - if so sell
                    if position:
                        # close the position
                        self.__liquidate_position(position, current_day_index)
                    # exit the loop as a precaution
                    break

            # update the progress
            if progress_observer is not None:
                progress_observer.update_progress(increment)

        # add the buys and sells to the df
        self.__add_buys_sells()

        # get the chopped DataFrame
        chopped_temp_df = self.__data_manager.get_chopped_df(sim_window_start_day)

        log.info('Simulation complete!')

        # initiate an analyzer with the positions data
        analyzer = SimulationAnalyzer(self.__single_simulation_position_archive)

        end_time = perf_counter()
        elapsed_time = round(end_time - start_time, 4)

        # elapsed_time, trade_count, effectiveness, avg_pl, total_pl
        self.__log_results(elapsed_time, analyzer.total_trades(), analyzer.effectiveness(), analyzer.avg_profit_loss(),
                           analyzer.total_profit_loss(), 'N/A')

        if not self.__running_multiple:
            self.__print_singular_results(elapsed_time, analyzer.total_trades(), analyzer.effectiveness(),
                                          analyzer.avg_profit_loss(),
                                          analyzer.total_profit_loss(), 'N/A')

        if self.__reporting_on:
            # create an export object
            exporter = Exporter()
            # synchronous charting
            exporter.export(chopped_temp_df, self.__symbol)

        chart_filepath = ''

        if show_chart or save_option:
            # create the display object
            display = SingularDisplay(self.__indicators.values())
            chart_filepath = display.chart(chopped_temp_df, self.__symbol, show_chart, save_option)

        return {
            'symbol': self.__symbol,
            'elapsed_time': elapsed_time,
            'trades_made': len(self.__single_simulation_position_archive),
            'effectiveness': analyzer.effectiveness(),
            'average_profit_loss': analyzer.avg_profit_loss(),
            'total_profit_loss': self.__account.get_profit_loss(),
            'account_value': self.__account.get_balance(),
            'chart_filepath': chart_filepath
        }

    def run_multiple(self,
                     symbols: list,
                     show_individual_charts=False,
                     save_individual_charts=False,
                     show_chart=True,
                     save_option=Display.TEMP_SAVE,
                     progress_observer=None) -> dict:
        """Simulate a list of assets.

        Args:
            symbols (list): The list of assets to simulation.
            show_individual_charts (bool): Show a chart for each symbol.
            save_individual_charts (bool): Save the chart for each symbol.
            show_chart (bool): Show the chart when finished.
            save_option (int): Save the chart when finished.
            progress_observer (any): Observer object to update progress to.
        """
        start_time = perf_counter()

        # disable printing for TQDM
        self.__running_multiple = True

        # reset the multiple simulation archived symbols to clear any data from previous multiple simulations
        self.__multiple_simulation_position_archive = []

        # calculate the increment for the progress bar
        increment = 1.0  # must supply default value
        if progress_observer is not None:
            increment = 100.0 / float(len(symbols))

        # simulate each symbol
        results = []
        for symbol in tqdm(symbols, f'Simulating {len(symbols)} symbols'):
            try:
                # run the simulation for that symbol
                result = self.run(symbol, show_individual_charts, save_individual_charts)
                # capture the archived positions from the symbol run in the multiple positions list
                self.__multiple_simulation_position_archive += self.__single_simulation_position_archive
            except Exception as e:
                print(f'\nException {e} caught trying to simulate symbol: {symbol}, skipping...')
                continue
            results.append(result)

            # update the progress
            if progress_observer is not None:
                progress_observer.update_progress(increment)

        # re-enable printing for TQDM
        self.__running_multiple = False
        # save the results in case the user wants to write them to file
        self.__stored_results = results

        # initiate an analyzer with the positions data
        analyzer = SimulationAnalyzer(self.__multiple_simulation_position_archive)

        chart_filepath = ''
        if show_chart or save_option:
            # create the display object
            display = MultipleDisplay()
            chart_filepath = display.chart(results, show_chart, save_option)

        end_time = perf_counter()
        elapsed_time = round(end_time - start_time, 4)

        return {
            'elapsed_time': elapsed_time,
            'trades_made': analyzer.total_trades(),
            'effectiveness': analyzer.effectiveness(),
            'average_profit_loss': analyzer.avg_profit_loss(),
            'total_profit_loss': analyzer.total_profit_loss(),
            'chart_filepath': chart_filepath
        }

    def __reset_singular_attributes(self):
        self.__account.reset()
        self.__buy_list = []
        self.__sell_list = []
        self.__single_simulation_position_archive = []

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

        additional_days = self.__trigger_manager.calculate_strategy_timestamps()

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

        self.__trigger_manager.parse_strategy_rules(self.__data_manager)

    def __add_buys_sells(self):
        """Adds the buy and sell lists to the DataFrame."""
        self.__data_manager.add_column('Buy', self.__buy_list)
        self.__data_manager.add_column('Sell', self.__sell_list)

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
        _buy_price = self.__data_manager.get_data_point(self.__data_manager.CLOSE, current_day_index)

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
        _sell_price = float(self.__data_manager.get_data_point(self.__data_manager.CLOSE, current_day_index))

        # close the position
        position.close_position(_sell_price)

        # add the position to the archive
        self.__single_simulation_position_archive.append(position)

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

    @staticmethod
    def __log_details(symbol, start, end, focus_days, tradable_days, balance):
        log.info('==== Simulation Details =====')
        log.info(f'Symbol          : {symbol}')
        log.info(f'Start Date      : {start}')
        log.info(f'End Date        : {end}')
        log.info(f'Window Size     : {focus_days}')
        log.info(f'Trade-able Days : {tradable_days}')
        log.info(f'Account Value   : ${balance}')
        log.info('=============================')

    @staticmethod
    def __log_results(elapsed_time, trade_count, effectiveness, avg_pl, total_pl, account_value):
        log.info('====== Simulation Results ======')
        log.info(f'Elapsed time  : {elapsed_time} seconds')
        log.info(f'Trades made   : {trade_count}')
        log.info(f'Effectiveness : {effectiveness}%')
        log.info(f'Avg. P/L      : ${avg_pl}')
        log.info(f'Total P/L     : ${total_pl}')
        log.info(f'Account Value : ${account_value}')
        log.info('================================')

    @staticmethod
    def __print_singular_results(elapsed_time, trade_count, effectiveness, avg_pl, total_pl, account_value):
        """Prints the simulation results."""
        print('====== Simulation Results ======')
        print(f'Elapsed time  : {elapsed_time} seconds')
        print(f'Trades made   : {trade_count}')
        print(f'Effectiveness : {effectiveness}%')
        print(f'Avg. P/L      : ${avg_pl}')
        print(f'Total P/L     : ${total_pl}')
        print(f'Account Value : ${account_value}')
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
