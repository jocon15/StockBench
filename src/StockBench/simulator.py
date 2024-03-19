import os
import time
import math
import logging
from tqdm import tqdm
from time import perf_counter
from datetime import datetime
from StockBench.constants import *
from StockBench.broker.broker import Broker
from StockBench.export.export import Exporter
from StockBench.display.display import Display
from StockBench.position.position import Position
from StockBench.display.singular import SingularDisplay
from StockBench.display.multiple import MultipleDisplay
from StockBench.account.user_account import UserAccount
from StockBench.analysis.analyzer import SimulationAnalyzer
from StockBench.trigger.trigger_manager import TriggerManager
from StockBench.function_tools.nonce import datetime_timestamp
from StockBench.simulation_data.data_manager import DataManager
from StockBench.indicators.indicator_manager import IndicatorManager

log = logging.getLogger()


class Simulator:
    """
    Breakdown of the simulation data compared to the simulation window:

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
        """
        Args:
            balance (float): The initial balance for the account.
        """
        # dependencies
        self.__account = UserAccount(balance)
        self.__broker = Broker()
        self.__data_manager = None  # gets constructed once we request the data
        self.__trigger_manager = None  # gets constructed once we have the strategy
        self.__indicators = IndicatorManager.load_indicators()

        # simulation settings
        self.__strategy = None
        self.__start_date_unix = None
        self.__end_date_unix = None
        self.__augmented_start_date_unix = None

        # positions storage during simulation
        self.__single_simulation_position_archive = []
        self.__multiple_simulation_position_archive = []

        # post-simulation settings
        self.__reporting_on = False
        self.__running_multiple = False

        # have not implemented stored results yet
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
        user_logging_filepath = os.path.join(self.__logs_folder, f'RunLog_{datetime_timestamp()}')

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
        developer_logging_filepath = os.path.join(self.__dev_folder, f'DevLog_{datetime_timestamp()}')

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
            save_option (int): Selection for how to save the finished chart.
            progress_observer (any): Observer object to update progress to.
        """
        start_time = perf_counter()

        # broker only excepts capitalized symbols
        symbol = symbol.upper()

        # perform the pre-simulation tasks
        (total_days, days_in_focus, sim_window_start_day,
         trade_able_days, increment) = self.__pre_process(symbol, progress_observer)

        log.info(f'Beginning simulation...')

        # ===================== Simulation Loop ======================
        buy_mode = True
        position = None
        # Loop from the focus start day (ex. 200) to the total amount of days in the set (ex. 400).
        for current_day_index in range(sim_window_start_day, self.__data_manager.get_data_length()):
            # simulate the current day
            buy_mode, position = self.__simulate_day(current_day_index, buy_mode, position, progress_observer,
                                                     increment)
        # ============================================================

        log.info('Simulation complete!')

        return self.__post_process(symbol, sim_window_start_day, start_time, show_chart, save_option)

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

        increment = self.__multi_pre_process(symbols, progress_observer)

        # simulate each symbol
        results = []
        for symbol in tqdm(symbols, f'Simulating {len(symbols)} symbols'):
            # run the simulation for that symbol
            result = self.run(symbol, show_individual_charts, save_individual_charts)
            # capture the archived positions from the symbol run in the multiple positions list
            self.__multiple_simulation_position_archive += self.__single_simulation_position_archive

            results.append(result)

            # update the progress
            if progress_observer is not None:
                progress_observer.update_progress(increment)

        return self.__multi_post_process(results, start_time, show_chart, save_option)

    def __pre_process(self, symbol, progress_observer) -> tuple:
        """Setup for the simulation."""
        log.info(f'Setting up simulation for symbol: {symbol}...')

        # reset the attributes()
        self.__reset_singular_attributes()

        # check the strategy for errors
        self.__basic_error_check_strategy()

        # parse the strategy for timestamps, so we know what the user wants
        self.__check_strategy_timestamps()

        # get the data from the broker
        temp_df = self.__broker.get_daily_data(symbol,
                                               self.__augmented_start_date_unix,
                                               self.__end_date_unix)

        # initialize the data api with the broker data
        self.__data_manager = DataManager(temp_df)

        # add indicators to the data based on strategy
        self.__trigger_manager.add_indicator_data(self.__data_manager)

        # print the header if necessary
        if not self.__running_multiple:
            self.__print_header(symbol)

        # calculate the simulation window
        total_days, days_in_focus, sim_window_start_day, trade_able_days = self.__calculate_simulation_window()

        # calculate the increment for the progress bar
        increment = 1.0  # must supply default value
        if progress_observer is not None:
            increment = 100.0 / (self.__data_manager.get_data_length() - sim_window_start_day)

        log.info(f'Setup for symbol: {symbol} complete')

        self.__log_details(symbol, self.__unix_to_string(self.__start_date_unix),
                           self.__unix_to_string(self.__end_date_unix), days_in_focus, trade_able_days,
                           self.__account.get_balance())

        return total_days, days_in_focus, sim_window_start_day, trade_able_days, increment

    def __simulate_day(self, current_day_index, buy_mode, position, progress_observer, increment) -> tuple:
        """Core simulation logic for simulating 1 day."""
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

        # update the progress
        if progress_observer is not None:
            progress_observer.update_progress(increment)

        return buy_mode, position

    def __post_process(self, symbol, sim_window_start_day, start_time, show_chart, save_option) -> dict:
        """Cleanup and analysis after the simulation."""
        # add the buys and sells to the df
        self.__add_positions_to_data()

        # get the chopped DataFrame
        chopped_temp_df = self.__data_manager.get_chopped_df(sim_window_start_day)

        # initiate an analyzer with the positions data
        analyzer = SimulationAnalyzer(self.__single_simulation_position_archive)

        end_time = perf_counter()
        elapsed_time = round(end_time - start_time, 4)

        self.__log_results(elapsed_time, analyzer, self.__account.get_balance())

        if not self.__running_multiple:
            self.__print_singular_results(elapsed_time, analyzer, self.__account.get_balance())

        if self.__reporting_on:
            # create an export object
            exporter = Exporter()
            # synchronous charting
            exporter.export(chopped_temp_df, symbol)

        chart_filepath = ''
        if show_chart or save_option:
            # create the display object
            display = SingularDisplay(self.__indicators.values())
            chart_filepath = display.chart(chopped_temp_df, symbol, show_chart, save_option)

        return {
            'symbol': symbol,
            'elapsed_time': elapsed_time,
            'trades_made': analyzer.total_trades(),
            'effectiveness': analyzer.effectiveness(),
            'total_profit_loss': analyzer.total_profit_loss(),
            'average_profit_loss': analyzer.average_profit_loss(),
            'median_profit_loss': analyzer.median_profit_loss(),
            'standard_profit_loss_deviation': analyzer.standard_profit_loss_deviation(),
            'account_value': self.__account.get_balance(),
            'chart_filepath': chart_filepath
        }

    def __multi_pre_process(self, symbols, progress_observer) -> float:
        # disable printing for TQDM
        self.__running_multiple = True

        # reset the multiple simulation archived symbols to clear any data from previous multiple simulations
        self.__multiple_simulation_position_archive = []

        # calculate the increment for the progress bar
        increment = 1.0  # must supply default value
        if progress_observer is not None:
            increment = 100.0 / float(len(symbols))

        return increment

    def __multi_post_process(self, results, start_time, show_chart, save_option):
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
            'total_profit_loss': analyzer.total_profit_loss(),
            'average_profit_loss': analyzer.average_profit_loss(),
            'median_profit_loss': analyzer.median_profit_loss(),
            'standard_profit_loss_deviation': analyzer.standard_profit_loss_deviation(),
            'chart_filepath': chart_filepath
        }

    def __reset_singular_attributes(self):
        """Clear singular simulation stored data."""
        self.__account.reset()
        self.__single_simulation_position_archive = []

    def __basic_error_check_strategy(self):
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

    def __check_strategy_timestamps(self):
        """Parse the strategy for relevant information needed to make the API request."""
        log.debug('Parsing strategy for timestamps...')
        if 'start' in self.__strategy.keys():
            self.__start_date_unix = int(self.__strategy['start'])
        if 'end' in self.__strategy.keys():
            self.__end_date_unix = int(self.__strategy['end'])

        additional_days = self.__trigger_manager.get_additional_days()

        # add a buffer
        if additional_days != 0:
            # we figure 2 weekdays and a holiday for every week of additional days
            # since it gets cast to int, the decimal is cut off -> it's usually < 3 per week after cast
            additional_days += int((additional_days / 7) * 3)
        # now, we should always have enough days to supply the indicators that the user requires

        self.__error_check_timestamps(self.__start_date_unix, self.__end_date_unix)
        self.__augmented_start_date_unix = self.__start_date_unix - (additional_days * SECONDS_1_DAY)

    def __calculate_simulation_window(self) -> tuple:
        """Calculate window dimensions."""
        total_days = int((self.__end_date_unix - self.__augmented_start_date_unix) / SECONDS_1_DAY)
        days_in_focus = int((self.__end_date_unix - self.__start_date_unix) / SECONDS_1_DAY)
        sim_window_start_day = total_days - days_in_focus
        trade_able_days = self.__data_manager.get_data_length() - sim_window_start_day

        return total_days, days_in_focus, sim_window_start_day, trade_able_days

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

        log.info('Position created successfully')

        # build and return the new position
        return Position(_buy_price, share_count, current_day_index)

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
        position.close_position(_sell_price, current_day_index)

        # add the position to the archive
        self.__single_simulation_position_archive.append(position)

        # calculate the deposit amount
        deposit_amount = round(_sell_price * position.get_share_count(), 3)

        log.info('Position closed successfully')

        # deposit the value of the position to the account
        self.__account.deposit(deposit_amount)

    def __add_positions_to_data(self):
        """Add the position data to the simulation data."""
        # initialize the lists to the length of the simulation (with None values)
        acquisition_price_list = [None for _ in range(self.__data_manager.get_data_length())]
        liquidation_price_list = [None for _ in range(self.__data_manager.get_data_length())]

        # fill in the list values with the position data
        for position in self.__single_simulation_position_archive:
            acquisition_price_list[position.buy_day_index] = position.get_buy_price()
            liquidation_price_list[position.sell_day_index] = position.get_sell_price()

        # add the columns to the data
        self.__data_manager.add_column('Buy', acquisition_price_list)
        self.__data_manager.add_column('Sell', liquidation_price_list)

    @staticmethod
    def __print_header(symbol):
        """Prints the simulation header."""
        print('======= Simulation Start =======')
        print(f'Running simulation on {symbol}...')
        print('================================')

    @staticmethod
    def __log_details(symbol, start, end, focus_days, tradable_days, balance):
        log.info('==== Simulation Details =====')
        log.info(f'Symbol          : {symbol}')
        log.info(f'Start Date      : {start}')
        log.info(f'End Date        : {end}')
        log.info(f'Window Size     : {focus_days}')
        log.info(f'Trade-able Days : {tradable_days}')
        log.info(f'Account Value   : $ {balance}')
        log.info('=============================')

    @staticmethod
    def __log_results(elapsed_time, analyzer: SimulationAnalyzer, balance):
        log.info('====== Simulation Results ======')
        log.info(f'Elapsed Time  : {elapsed_time} seconds')
        log.info(f'Trades Made   : {analyzer.total_trades()}')
        log.info(f'Effectiveness : {analyzer.effectiveness()}%')
        log.info(f'Total P/L     : $ {analyzer.total_profit_loss()}')
        log.info(f'Average P/L   : $ {analyzer.average_profit_loss()}')
        log.info(f'Median P/L    : $ {analyzer.median_profit_loss()}')
        log.info(f'Stddev P/L    : $ {analyzer.standard_profit_loss_deviation()}')
        log.info(f'Account Value : $ {balance}')
        log.info('================================')

    @staticmethod
    def __print_singular_results(elapsed_time, analyzer: SimulationAnalyzer, balance):
        """Prints the simulation results."""
        print('====== Simulation Results ======')
        print(f'Elapsed Time  : {elapsed_time} seconds')
        print(f'Trades Made   : {analyzer.total_trades()}')
        print(f'Effectiveness : {analyzer.effectiveness()}%')
        print(f'Total P/L     : $ {analyzer.total_profit_loss()}')
        print(f'Average P/L   : $ {analyzer.average_profit_loss()}')
        print(f'Median P/L    : $ {analyzer.median_profit_loss()}')
        print(f'Stddev P/L    : $ {analyzer.standard_profit_loss_deviation()}')
        print(f'Account Value : $ {balance}')
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
