import os
import sys
import time
import math
import logging
from tqdm import tqdm
from time import perf_counter
from datetime import datetime
from StockBench.constants import *
from StockBench.broker.broker import Broker
from StockBench.export.window_data_exporter import WindowDataExporter
from StockBench.position.position import Position
from concurrent.futures import ProcessPoolExecutor
from StockBench.charting.charting_engine import ChartingEngine
from StockBench.charting.singular.singular_charting_engine import SingularChartingEngine
from StockBench.charting.multi.multi_charting_engine import MultiChartingEngine
from StockBench.account.user_account import UserAccount
from StockBench.analysis.analyzer import SimulationAnalyzer
from StockBench.algorithm.algorithm import Algorithm
from StockBench.function_tools.timestamp import datetime_timestamp
from StockBench.simulation_data.data_manager import DataManager
from StockBench.indicators.indicator_manager import IndicatorManager
from StockBench.logging_handlers.handlers import ProgressMessageHandler

# generic logger used for debugging the application
log = logging.getLogger()

# logger dedicated to logging messages to the gui terminal
gui_terminal_log = logging.getLogger('gui_terminal_logging')


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
    LOGS_FOLDER = 'logs'
    DEV_FOLDER = 'dev'

    CHARTS_AND_DATA = 0
    DATA_ONLY = 1

    def __init__(self, initial_balance: float):
        """
        Args:
            initial_balance (float): The initial balance for the account.
        """
        # dependencies
        self.__account = UserAccount(initial_balance)
        self.__broker = Broker()
        self.__data_manager = None  # gets constructed once we request the data
        self.__algorithm = None  # gets constructed once we have the strategy
        self.__available_indicators = IndicatorManager.load_indicators()

        # simulation settings
        self.__algorithm = None

        # positions storage during simulation
        self.__single_simulation_position_archive = []
        self.__multiple_simulation_position_archive = []

        # post-simulation settings
        self.__reporting_on = False
        self.__running_multiple = False
        self.__running_as_exe = getattr(sys, 'frozen', False)

    def enable_logging(self):
        """Enable user logging_handlers."""
        # set the logging_handlers level to info
        log.setLevel(logging.INFO)

        # build the filepath
        user_logging_filepath = os.path.join(self.LOGS_FOLDER, f'RunLog_{datetime_timestamp()}')

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
        """Enable developer logging_handlers.

        Args:
            level (int): The logging_handlers level for the logger.
        """
        # set the logging_handlers level
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
        developer_logging_filepath = os.path.join(self.DEV_FOLDER, f'DevLog_{datetime_timestamp()}')

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
        # build the algorithm using the strategy
        self.__algorithm = Algorithm(strategy, self.__available_indicators.values())

    def run(self, symbol: str, results_depth=CHARTS_AND_DATA, save_option=ChartingEngine.TEMP_SAVE,
            progress_observer=None) -> dict:
        """Run a simulation on an asset.

        Args:
            symbol (str): The symbol to run the simulation on.
            results_depth (bool): Show the chart when finished.
            save_option (int): Selection for how to save the finished chart.
            progress_observer (any): Observer object to update progress to.
        """
        start_time = perf_counter()

        if not self.__running_multiple:
            if progress_observer:
                # enable the progress message handler to capture the logs
                gui_terminal_log.setLevel(logging.INFO)
                gui_terminal_log.addHandler(ProgressMessageHandler(progress_observer))

            log.info(f'Using strategy: {self.__algorithm.strategy_filename}')
            gui_terminal_log.info(f'Using strategy: {self.__algorithm.strategy_filename}')

        log.info(f'Starting simulation for symbol: {symbol}...')
        gui_terminal_log.info(f'Starting simulation for {symbol}...')

        # broker only excepts capitalized symbols
        symbol = symbol.upper()

        # perform the pre-simulation tasks
        sim_window_start_day, trade_able_days, increment = self.__pre_process(symbol, progress_observer)

        # ===================== Simulation Loop ======================
        buy_mode = True
        position = None
        # Loop from the focus start day (ex. 200) to the total amount of days in the set (ex. 400).
        for current_day_index in range(sim_window_start_day, self.__data_manager.get_data_length()):
            # simulate the current day
            buy_mode, position = self.__simulate_day(current_day_index, buy_mode, position, progress_observer,
                                                     increment)
        # ============================================================

        gui_terminal_log.info(f'Simulation for {symbol} complete')

        return self.__post_process(symbol, trade_able_days, sim_window_start_day, start_time, results_depth,
                                   save_option, progress_observer)

    def run_multiple(self,
                     symbols: list,
                     results_depth=CHARTS_AND_DATA,
                     save_option=ChartingEngine.TEMP_SAVE,
                     progress_observer=None) -> dict:
        """Simulate a list of assets.

        Args:
            symbols (list): The list of assets to simulation.
            results_depth (bool): Switch to remove charts from results.
            save_option (int): Save the chart when finished.
            progress_observer (any): Observer object to update progress to.
        """
        start_time = perf_counter()

        if progress_observer:
            # enable the progress message handler to capture the logs
            gui_terminal_log.setLevel(logging.INFO)
            gui_terminal_log.addHandler(ProgressMessageHandler(progress_observer))

        gui_terminal_log.info('Beginning multiple symbol simulation...')

        log.info(f'Using strategy: {self.__algorithm.strategy_filename}')
        gui_terminal_log.info(f'Using strategy: {self.__algorithm.strategy_filename}')

        progress_bar_increment = self.__multi_pre_process(symbols, progress_observer)

        tqdm_increment = 0
        pbar = None
        if not self.__running_as_exe:
            # tqdm only works if running as python file
            tqdm_increment = round(100.0 / len(symbols), 2)
            pbar = tqdm(total=100)

        # simulate each symbol
        results = []
        for symbol in symbols:
            # run the simulation for that symbol
            result = self.run(symbol=symbol, results_depth=results_depth, save_option=save_option)
            # capture the archived positions from the symbol run in the multiple positions list
            self.__multiple_simulation_position_archive += self.__single_simulation_position_archive

            results.append(result)

            # update the progress observer
            if progress_observer:
                progress_observer.update_progress(progress_bar_increment)

            # update tqdm if enabled
            if not self.__running_as_exe:
                pbar.update(tqdm_increment)

        log.info('Multi-simulation complete')
        gui_terminal_log.info('Multiple symbol simulation complete')

        return self.__multi_post_process(results, start_time, results_depth,
                                         save_option, progress_observer)

    def __pre_process(self, symbol, progress_observer) -> tuple:
        """Setup for the simulation."""
        log.info(f'Setting up simulation for symbol: {symbol}...')

        # reset the attributes()
        self.__reset_singular_attributes()

        # parse the strategy for timestamps
        start_date_unix, end_date_unix, additional_days = self.__algorithm.get_window()
        augmented_start_date_unix = start_date_unix - (additional_days * SECONDS_1_DAY)

        # get the data from the broker
        temp_df = self.__broker.get_daily_data(symbol, augmented_start_date_unix, end_date_unix)

        # initialize the data api with the broker data
        self.__data_manager = DataManager(temp_df)

        # add indicators to the data based on strategy
        self.__algorithm.add_indicator_data(self.__data_manager)

        # print the header if necessary
        if not self.__running_multiple:
            self.__print_header(symbol)

        # calculate the simulation window
        total_days, days_in_focus, sim_window_start_day, trade_able_days = (
            self.__calculate_simulation_window(start_date_unix, end_date_unix, augmented_start_date_unix,
                                               self.__data_manager))

        # calculate the increment for the progress bar
        increment = 1.0  # must supply default value
        if progress_observer is not None:
            increment = 100.0 / (self.__data_manager.get_data_length() - sim_window_start_day)

        log.info(f'Setup for symbol: {symbol} complete')

        self.__log_details(self.__algorithm.strategy_filename, symbol, self.__unix_to_string(start_date_unix),
                           self.__unix_to_string(end_date_unix), days_in_focus, trade_able_days,
                           self.__account.get_balance())

        return sim_window_start_day, trade_able_days, increment

    def __simulate_day(self, current_day_index, buy_mode, position, progress_observer, increment) -> tuple:
        """Core simulation logic for simulating 1 day."""
        log.debug(f'Current day index: {current_day_index}')

        if current_day_index == self.__data_manager.get_data_length() - 1:
            # check that position still exists - if so sell
            if position:
                # the position is still open at the end of the simulation
                log.info('Position closed due to end of simulation reached')
                # close the position
                self.__liquidate_position(position, current_day_index, 'end of simulation window')
        else:
            # current day is not the end of the simulation (free to buy and sell)
            if buy_mode:
                was_triggered, rule = self.__algorithm.check_triggers_by_side(BUY_SIDE, self.__data_manager,
                                                                              current_day_index, None)
                if was_triggered:
                    # create a position
                    position = self.__create_position(current_day_index, rule)
                    # switch to selling
                    buy_mode = False
            else:
                # sell mode
                was_triggered, rule = self.__algorithm.check_triggers_by_side(SELL_SIDE, self.__data_manager,
                                                                              current_day_index, position)
                if was_triggered:
                    # close the position
                    self.__liquidate_position(position, current_day_index, rule)
                    # clear the stored position
                    position = None
                    # switch to buying
                    buy_mode = True

                elif current_day_index == self.__data_manager.get_data_length() - 1:
                    # the position is still open at the end of the simulation
                    log.info('Position closed due to end of simulation reached')
                    # check that position still exists - if so sell
                    if position:
                        # close the position
                        self.__liquidate_position(position, current_day_index, rule)

            # update the progress observer by 1 increment
            if progress_observer is not None:
                progress_observer.update_progress(increment)

        return buy_mode, position

    def __post_process(self, symbol, trade_able_days, sim_window_start_day, start_time, results_depth,
                       save_option, progress_observer) -> dict:
        """Cleanup and analysis after the simulation."""
        gui_terminal_log.info(f'Starting analytics for {symbol}...')
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
            exporter = WindowDataExporter()
            # synchronous charting
            exporter.export(chopped_temp_df, symbol)

        overview_chart_filepath = ''
        buy_rules_chart_filepath = ''
        sell_rules_chart_filepath = ''
        positions_duration_bar_chart_filepath = ''
        positions_profit_loss_bar_chart_filepath = ''
        positions_profit_loss_histogram_chart_filepath = ''
        if results_depth == self.CHARTS_AND_DATA:
            # faster to do it synchronously for singular
            gui_terminal_log.info('Building overview chart...')
            overview_chart_filepath = SingularChartingEngine.build_indicator_chart(chopped_temp_df, symbol,
                                                                                   self.__available_indicators.values(),
                                                                                   save_option)

            gui_terminal_log.info('Building buy rules bar chart...')
            buy_rules_chart_filepath = ChartingEngine.build_rules_bar_chart(self.__single_simulation_position_archive,
                                                                            BUY_SIDE, symbol, save_option)

            gui_terminal_log.info('Building sell rules bar chart...')
            sell_rules_chart_filepath = ChartingEngine.build_rules_bar_chart(self.__single_simulation_position_archive,
                                                                             SELL_SIDE, symbol, save_option)

            gui_terminal_log.info('Building positions duration bar chart...')
            positions_duration_bar_chart_filepath = ChartingEngine.build_positions_duration_bar_chart(
                self.__single_simulation_position_archive, symbol, save_option)

            gui_terminal_log.info('Building positions profit loss bar chart...')
            positions_profit_loss_bar_chart_filepath = SingularChartingEngine.build_positions_profit_loss_bar_chart(
                self.__single_simulation_position_archive, symbol, save_option)

            gui_terminal_log.info('Building positions profit loss histogram chart...')
            positions_profit_loss_histogram_chart_filepath = ChartingEngine.build_positions_profit_loss_histogram_chart(
                self.__single_simulation_position_archive, self.__algorithm.strategy_filename, symbol, save_option)

        log.info('Simulation complete!')

        if not self.__running_multiple:
            gui_terminal_log.info(f'Analytics for {symbol} complete \u2705')
            if progress_observer:
                # inform the progress observer that the analytics is complete
                progress_observer.set_analytics_complete()
        else:
            gui_terminal_log.info(f'Analytics for {symbol} complete')

        return {
            STRATEGY_KEY: self.__algorithm.strategy_filename,
            SYMBOL_KEY: symbol,
            POSITIONS_KEY: self.__single_simulation_position_archive,
            TRADE_ABLE_DAYS_KEY: trade_able_days,
            ELAPSED_TIME_KEY: elapsed_time,
            TRADES_MADE_KEY: analyzer.total_trades(),
            AVERAGE_TRADE_DURATION_KEY: analyzer.average_trade_duration(),
            EFFECTIVENESS_KEY: analyzer.effectiveness(),
            TOTAL_PROFIT_LOSS_KEY: analyzer.total_profit_loss(),
            AVERAGE_PROFIT_LOSS_KEY: analyzer.average_profit_loss(),
            MEDIAN_PROFIT_LOSS_KEY: analyzer.median_profit_loss(),
            STANDARD_PROFIT_LOSS_DEVIATION_KEY: analyzer.standard_profit_loss_deviation(),
            ACCOUNT_VALUE_KEY: self.__account.get_balance(),
            OVERVIEW_CHART_FILEPATH_KEY: overview_chart_filepath,
            BUY_RULES_CHART_FILEPATH_KEY: buy_rules_chart_filepath,
            SELL_RULES_CHART_FILEPATH_KEY: sell_rules_chart_filepath,
            POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY: positions_duration_bar_chart_filepath,
            POSITIONS_PROFIT_LOSS_BAR_CHART_FILEPATH_KEY: positions_profit_loss_bar_chart_filepath,
            POSITIONS_PROFIT_LOSS_HISTOGRAM_CHART_FILEPATH_KEY: positions_profit_loss_histogram_chart_filepath
        }

    def __multi_pre_process(self, symbols, progress_observer) -> float:
        log.debug('Running multi simulation pre-process...')
        # disable printing for TQDM
        self.__running_multiple = True

        # reset the multiple simulation archived symbols to clear any data from previous multiple simulations
        self.__multiple_simulation_position_archive = []

        # calculate the increment for the progress bar
        increment = 1.0  # must supply default value
        if progress_observer is not None:
            increment = 100.0 / float(len(symbols))

        return increment

    def __multi_post_process(self, results, start_time, results_depth, save_option, progress_observer):
        # re-enable printing for TQDM
        log.info('Running multi simulation post-process...')
        gui_terminal_log.info('Starting analytics...')
        self.__running_multiple = False
        # save the results in case the user wants to write them to file
        self.__stored_results = results

        # initiate an analyzer with the positions data
        analyzer = SimulationAnalyzer(self.__multiple_simulation_position_archive)

        overview_chart_filepath = ''
        buy_rules_chart_filepath = ''
        sell_rules_chart_filepath = ''
        positions_duration_bar_chart_filepath = ''
        positions_profit_loss_bar_chart_filepath = ''
        positions_profit_loss_histogram_chart_filepath = ''
        if results_depth == self.CHARTS_AND_DATA:
            with ProcessPoolExecutor() as executor:
                gui_terminal_log.info('Building overview chart...')
                future1 = executor.submit(MultiChartingEngine.build_overview_chart, results,
                                          self.__account.get_initial_balance(), save_option)

                gui_terminal_log.info('Building buy rules bar chart...')
                future2 = executor.submit(ChartingEngine.build_rules_bar_chart,
                                          self.__single_simulation_position_archive, BUY_SIDE, None, save_option)

                gui_terminal_log.info('Building sell rules bar chart...')
                future3 = executor.submit(ChartingEngine.build_rules_bar_chart,
                                          self.__single_simulation_position_archive, SELL_SIDE, None, save_option)

                gui_terminal_log.info('Building positions duration bar chart...')
                future4 = executor.submit(ChartingEngine.build_positions_duration_bar_chart,
                                          self.__single_simulation_position_archive, None, save_option)

                gui_terminal_log.info('Building positions profit loss bar chart...')
                future5 = executor.submit(ChartingEngine.build_positions_profit_loss_bar_chart,
                                          self.__single_simulation_position_archive, None, save_option)

                gui_terminal_log.info('Building positions profit loss histogram chart...')
                future6 = executor.submit(ChartingEngine.build_positions_profit_loss_histogram_chart,
                                          self.__single_simulation_position_archive, self.__algorithm.strategy_filename,
                                          None, save_option)

                overview_chart_filepath = future1.result()
                buy_rules_chart_filepath = future2.result()
                sell_rules_chart_filepath = future3.result()
                positions_duration_bar_chart_filepath = future4.result()
                positions_profit_loss_bar_chart_filepath = future5.result()
                positions_profit_loss_histogram_chart_filepath = future6.result()

        end_time = perf_counter()
        elapsed_time = round(end_time - start_time, 4)

        gui_terminal_log.info('Analytics complete \u2705')

        if progress_observer:
            # inform the progress observer that the analytics is complete
            progress_observer.set_analytics_complete()

        return {
            STRATEGY_KEY: self.__algorithm.strategy_filename,
            POSITIONS_KEY: self.__multiple_simulation_position_archive,
            TRADE_ABLE_DAYS_KEY: results[0][TRADE_ABLE_DAYS_KEY],
            ELAPSED_TIME_KEY: elapsed_time,
            TRADES_MADE_KEY: analyzer.total_trades(),
            AVERAGE_TRADE_DURATION_KEY: analyzer.average_trade_duration(),
            EFFECTIVENESS_KEY: analyzer.effectiveness(),
            TOTAL_PROFIT_LOSS_KEY: analyzer.total_profit_loss(),
            AVERAGE_PROFIT_LOSS_KEY: analyzer.average_profit_loss(),
            MEDIAN_PROFIT_LOSS_KEY: analyzer.median_profit_loss(),
            STANDARD_PROFIT_LOSS_DEVIATION_KEY: analyzer.standard_profit_loss_deviation(),
            OVERVIEW_CHART_FILEPATH_KEY: overview_chart_filepath,
            BUY_RULES_CHART_FILEPATH_KEY: buy_rules_chart_filepath,
            SELL_RULES_CHART_FILEPATH_KEY: sell_rules_chart_filepath,
            POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY: positions_duration_bar_chart_filepath,
            POSITIONS_PROFIT_LOSS_BAR_CHART_FILEPATH_KEY: positions_profit_loss_bar_chart_filepath,
            POSITIONS_PROFIT_LOSS_HISTOGRAM_CHART_FILEPATH_KEY: positions_profit_loss_histogram_chart_filepath
        }

    def __reset_singular_attributes(self):
        """Clear singular simulation stored data."""
        self.__account.reset()
        self.__single_simulation_position_archive = []

    def __create_position(self, current_day_index: int, rule: str) -> Position:
        """Creates a position and updates the account.

        Args:
            current_day_index (int): The index of the current day
            rule (str): The strategy rule used to acquire the position.

        return:
            Position: The created Position object.

        Notes:
            The assumption is that the user wants to use full buying power (for now)
        """
        log.info('Creating the position...')

        # add the buying price to the DataFrame
        buy_price = self.__data_manager.get_data_point(self.__data_manager.CLOSE, current_day_index)

        # calculate the withdrawal amount (nearest whole share - floor direction)
        share_count = float(math.floor(self.__account.get_balance() / buy_price))

        # create the new position
        new_position = Position(buy_price, share_count, current_day_index, rule)

        log.info('Position created successfully')

        # withdraw the money from the account
        self.__account.withdraw(round(buy_price * share_count, 3))

        return new_position

    def __liquidate_position(self, position: Position, current_day_index: int, rule: str):
        """Closes the position and updates the account.

        Args:
            position (Position): The position to close.
            current_day_index (int): The index of the current day
            rule (str): The strategy key used to acquire the position.
        """
        log.info('Closing the position...')

        # get the cosing price
        sell_price = float(self.__data_manager.get_data_point(self.__data_manager.CLOSE, current_day_index))

        # close the position
        position.close_position(sell_price, current_day_index, rule)

        if self.__is_stock_split(position, sell_price):
            gui_terminal_log.warning(f'Stock split avoided at day: {current_day_index}')
            log.info('Position excluded due to stock split!')
            # deposit the initial investment amount (undoing the withdrawal)
            self.__account.deposit(position.get_buy_price() * position.get_share_count())
            # skip adding the position to the list
            return

        # add the position to the archive
        self.__single_simulation_position_archive.append(position)

        log.info('Position closed successfully')

        # deposit the value of the position to the account
        self.__account.deposit(round(sell_price * position.get_share_count(), 3))

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
    def __calculate_simulation_window(start_date_unix: int, end_date_unix: int, augmented_start_date_unix: int,
                                      data_manager: DataManager) -> tuple:
        """Calculate window dimensions."""
        total_days = int((end_date_unix - augmented_start_date_unix) / SECONDS_1_DAY)
        days_in_focus = int((end_date_unix - start_date_unix) / SECONDS_1_DAY)
        sim_window_start_day = total_days - days_in_focus
        trade_able_days = data_manager.get_data_length() - sim_window_start_day

        return total_days, days_in_focus, sim_window_start_day, trade_able_days

    @staticmethod
    def __is_stock_split(position: Position, sell_price: float) -> bool:
        """Check if the position encountered a stock split."""
        if abs(position.profit_loss_percent(sell_price)) > STOCK_SPLIT_PLPC:
            return True
        return False

    @staticmethod
    def __print_header(symbol):
        """Prints the simulation header."""
        print('======= Simulation Start =======')
        print(f'Running simulation on {symbol}...')
        print('================================')

    @staticmethod
    def __log_details(filename, symbol, start, end, focus_days, tradable_days, balance):
        log.info('==== Simulation Details =====')
        log.info(f'Strategy        : {filename}')
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
