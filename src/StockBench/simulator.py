import os
import sys
import math
import logging

from pandas import DataFrame
from tqdm import tqdm
from time import perf_counter
from datetime import datetime
from typing import Optional, List, Tuple
from concurrent.futures import ProcessPoolExecutor

from StockBench.bundles.chart_path.multi_bundle import MultiSimulationChartPathBundle
from StockBench.bundles.chart_path.singular_bundle import SingularSimulationChartPathBundle
from StockBench.constants import *
from StockBench.broker.broker_client import BrokerClient
from StockBench.export.window_data_exporter import WindowDataExporter
from StockBench.factories.configuration import ClientConfigurationFactory
from StockBench.filesystem.fs_controller import FSController
from StockBench.observers.progress_observer import ProgressObserver
from StockBench.position.position import Position
from StockBench.charting.charting_engine import ChartingEngine
from StockBench.charting.singular.singular_charting_engine import SingularChartingEngine
from StockBench.charting.multi.multi_charting_engine import MultiChartingEngine
from StockBench.account.user_account import UserAccount
from StockBench.analysis.positions_analyzer import PositionsAnalyzer
from StockBench.algorithm.algorithm import Algorithm
from StockBench.function_tools.timestamp import datetime_timestamp
from StockBench.simulation_data.data_manager import DataManager
from StockBench.indicators.indicator_manager import IndicatorManager
from StockBench.logging_handlers.handlers import ProgressMessageHandler

# generic logger used for debugging the application
log = logging.getLogger()


class Simulator:
    """Encapsulates the simulation engine.

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

    def __init__(self, initial_balance: float, identifier: int = 1):
        """Constructor

        Args:
            initial_balance: The initial balance for the account.
        """
        # dependencies
        self.id = identifier
        self.__account = UserAccount(initial_balance)
        self.__broker = BrokerClient(ClientConfigurationFactory.create_broker_config())
        self.__data_manager = None  # gets constructed once we request the data
        self.__algorithm = None  # gets constructed once we have the strategy
        self.__available_indicators = IndicatorManager.load_indicators()

        # logger dedicated to logging messages to the gui status box (must be here to avoid log duplication)
        self.gui_status_log = logging.getLogger(f'gui_status_box_logging_{self.id}')

        # simulation settings
        self.__algorithm = None

        # positions storage during simulation
        self.__single_simulation_position_archive = []
        self.__multiple_simulation_position_archive = []
        self.__account_value_archive = []

        # post-simulation settings
        self.__reporting_on = False
        self.__running_multiple = False
        self.__running_as_exe = getattr(sys, 'frozen', False)

    def enable_logging(self) -> None:
        """Enable user logging_handlers."""
        log.setLevel(logging.INFO)
        user_logging_filepath = os.path.join(self.LOGS_FOLDER, f'RunLog_{datetime_timestamp()}')

        # make the directories if they don't already exist
        os.makedirs(os.path.dirname(user_logging_filepath), exist_ok=True)

        user_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')
        user_handler = logging.FileHandler(user_logging_filepath)
        user_handler.setFormatter(user_logging_formatter)
        log.addHandler(user_handler)

    def enable_developer_logging(self, level: int = 2) -> None:
        """Enable developer logging handlers."""
        if level == 1:
            log.setLevel(logging.DEBUG)
            developer_logging_formatter = logging.Formatter('%(funcName)s:%(lineno)d|%(levelname)s|%(message)s')
        elif level == 3:
            log.setLevel(logging.WARNING)
            developer_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')
        elif level == 4:
            log.setLevel(logging.ERROR)
            developer_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')
        elif level == 5:
            log.setLevel(logging.CRITICAL)
            developer_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')
        else:
            log.setLevel(logging.INFO)
            developer_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')

        developer_logging_filepath = os.path.join(self.DEV_FOLDER, f'DevLog_{datetime_timestamp()}')

        # make the directories if they don't already exist
        os.makedirs(os.path.dirname(developer_logging_filepath), exist_ok=True)

        developer_handler = logging.FileHandler(developer_logging_filepath)
        developer_handler.setFormatter(developer_logging_formatter)
        log.addHandler(developer_handler)

    def enable_reporting(self):
        """Enable report building."""
        self.__reporting_on = True

    def load_strategy(self, strategy: dict):
        """Load a strategy."""
        self.__algorithm = Algorithm(strategy, self.__available_indicators.values())

    def run(self, symbol: str, results_depth: int = CHARTS_AND_DATA,
            save_option: int = ChartingEngine.TEMP_SAVE, show_volume: bool = False, progress_observer=None) -> dict:
        """Run a simulation on a single asset."""
        start_time = perf_counter()

        # broker only excepts capitalized symbols
        symbol = symbol.upper()

        if not self.__running_multiple:
            if progress_observer:
                self.gui_status_log.setLevel(logging.INFO)
                self.gui_status_log.addHandler(ProgressMessageHandler(progress_observer))

            log.info(f'Using strategy: {self.__algorithm.strategy_filename}')
            self.gui_status_log.info(f'Using strategy: {self.__algorithm.strategy_filename}')

        log.info(f'Starting simulation for symbol: {symbol}...')
        self.gui_status_log.info(f'Starting simulation for {symbol}...')

        sim_window_start_day, trade_able_days, increment = self.__pre_process(symbol, progress_observer)

        # ===================== Simulation Loop ======================
        buy_mode = True
        position = None
        # loop from the window start day (ex. 200) to the total amount of days in the set (ex. 400)
        for current_day_index in range(sim_window_start_day, self.__data_manager.get_data_length()):
            buy_mode, position = self.__simulate_day(current_day_index, buy_mode, position, progress_observer,
                                                     increment)
        # ============================================================

        self.gui_status_log.info(f'Simulation for {symbol} complete')

        return self.__post_process(symbol, trade_able_days, sim_window_start_day, start_time, results_depth,
                                   save_option, show_volume, progress_observer)

    def run_multiple(self, symbols: List[str],
                     results_depth: int = CHARTS_AND_DATA,
                     save_option: int = ChartingEngine.TEMP_SAVE,
                     progress_observer: Optional[ProgressObserver] = None) -> dict:
        """Run a simulation on multiple assets."""
        start_time = perf_counter()

        if progress_observer:
            # enable the progress message handler to capture the logs
            self.gui_status_log.setLevel(logging.INFO)
            self.gui_status_log.addHandler(ProgressMessageHandler(progress_observer))

        self.gui_status_log.info('Beginning multiple symbol simulation...')

        log.info(f'Using strategy: {self.__algorithm.strategy_filename}')
        self.gui_status_log.info(f'Using strategy: {self.__algorithm.strategy_filename}')

        progress_bar_increment = self.__multi_pre_process(symbols, progress_observer)

        tqdm_increment = 0
        pbar = None
        if not self.__running_as_exe:
            # tqdm only works if running as python file
            tqdm_increment = round(100.0 / len(symbols), 2)
            pbar = tqdm(total=100)

        results = []
        for symbol in symbols:
            result = self.run(symbol=symbol, results_depth=results_depth, save_option=save_option)
            # capture the archived positions from the run in the multiple positions list
            self.__multiple_simulation_position_archive += self.__single_simulation_position_archive

            results.append(result)

            if progress_observer:
                progress_observer.update_progress(progress_bar_increment)

            if not self.__running_as_exe:
                pbar.update(tqdm_increment)

        log.info('Multi-simulation complete')
        self.gui_status_log.info('Multiple symbol simulation complete')

        return self.__multi_post_process(symbols, results, start_time, results_depth,
                                         save_option, progress_observer)

    def __pre_process(self, symbol: str, progress_observer: ProgressObserver) -> Tuple[int, int, float]:
        """Setup for the simulation."""
        log.info(f'Setting up simulation for symbol: {symbol}...')

        FSController.remove_temp_figures()

        self.__reset_singular_attributes()

        start_date_unix, end_date_unix, additional_days = self.__algorithm.get_simulation_window()
        augmented_start_date_unix = start_date_unix - (additional_days * SECONDS_1_DAY)

        temp_df = self.__broker.get_bars_data(symbol, augmented_start_date_unix, end_date_unix)

        self.__data_manager = DataManager(temp_df)

        self.__algorithm.add_indicator_data(self.__data_manager)

        if not self.__running_multiple:
            self.__print_header(symbol)

        total_days, days_in_focus, sim_window_start_day, trade_able_days = (
            self.__calculate_simulation_window(start_date_unix, end_date_unix, augmented_start_date_unix,
                                               self.__data_manager))

        increment = self.__calculate_progress_bar_increment(progress_observer, sim_window_start_day)

        log.info(f'Setup for symbol: {symbol} complete')

        self.__log_details(self.__algorithm.strategy_filename, symbol, self.__unix_to_string(start_date_unix),
                           self.__unix_to_string(end_date_unix), days_in_focus, trade_able_days,
                           self.__account.get_balance())

        return sim_window_start_day, trade_able_days, increment

    def __simulate_day(self, current_day_index: int, buy_mode: bool, position: Position,
                       progress_observer: ProgressObserver, increment: float) -> Tuple[bool, Position]:
        """Simulates trading on a single day."""
        log.debug(f'Current day index: {current_day_index}')

        if current_day_index == self.__data_manager.get_data_length() - 1:
            # reached the end of the simulation, if a position is still open, sell it
            if position:
                log.info('Position closed due to end of simulation reached')
                self.__liquidate_position(position, current_day_index, 'end of simulation window')
                position = None
        else:
            if buy_mode:
                was_triggered, rule = self.__algorithm.check_triggers_by_side(self.__data_manager, current_day_index,
                                                                              None, BUY_SIDE)
                if was_triggered:
                    position = self.__create_position(current_day_index, rule)
                    buy_mode = False  # switch to selling
            else:
                was_triggered, rule = self.__algorithm.check_triggers_by_side(self.__data_manager, current_day_index,
                                                                              position, SELL_SIDE)
                if was_triggered:
                    self.__liquidate_position(position, current_day_index, rule)
                    position = None
                    buy_mode = True  # switch to buying

            if progress_observer is not None:
                progress_observer.update_progress(increment)

        self.__record_day_end_account_value(position, current_day_index)

        return buy_mode, position

    def __record_day_end_account_value(self, position: Optional[Position], current_day_index: int) -> None:
        """Record the end of day account value."""
        account_value = self.__account.get_balance()
        if position:
            # if a position is currently open, add the position value to the account value
            # the account value will have a little left in it due to rounding
            current_price = self.__data_manager.get_data_point(self.__data_manager.CLOSE, current_day_index)
            position_value = round(position.get_share_count() * current_price, 2)
            account_value += position_value
        self.__account_value_archive.append(round(account_value, 2))

    def __post_process(self, symbol: str, trade_able_days: int, window_start_day: int, start_time: float,
                       results_depth: int, save_option: int, show_volume: bool,
                       progress_observer: ProgressObserver) -> dict:
        """Cleanup and analysis after a simulation."""
        self.gui_status_log.info(f'Starting analytics for {symbol}...')

        self.__add_positions_to_data()

        self.__add_account_values_to_data()

        chopped_temp_df = self.__data_manager.get_chopped_df(window_start_day)

        analyzer = PositionsAnalyzer(self.__single_simulation_position_archive)

        chart_paths_bundle = self.__create_singular_charts(symbol, chopped_temp_df, results_depth, save_option,
                                                           show_volume)

        end_time = perf_counter()
        elapsed_time = round(end_time - start_time, 4)

        self.__log_results(elapsed_time, analyzer, self.__account.get_balance())

        if not self.__running_multiple:
            self.__print_singular_results(elapsed_time, analyzer, self.__account.get_balance())

        if self.__reporting_on:
            exporter = WindowDataExporter()
            exporter.export(chopped_temp_df, symbol)

        log.info('Simulation complete!')

        if not self.__running_multiple:
            self.gui_status_log.info(f'Analytics for {symbol} complete \u2705')
            if progress_observer:
                # inform the progress observer that the analytics is complete
                progress_observer.set_analytics_complete()
        else:
            self.gui_status_log.info(f'Analytics for {symbol} complete')

        return {
            STRATEGY_KEY: self.__algorithm.strategy_filename,
            SYMBOL_KEY: symbol,
            SIMULATION_START_TIMESTAMP_KEY: self.__algorithm.strategy[START_KEY],
            SIMULATION_END_TIMESTAMP_KEY: self.__algorithm.strategy[END_KEY],
            INITIAL_ACCOUNT_VALUE_KEY: self.__account.get_initial_balance(),
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
            OVERVIEW_CHART_FILEPATH_KEY: chart_paths_bundle.overview_chart_filepath,
            BUY_RULES_CHART_FILEPATH_KEY: chart_paths_bundle.buy_rules_chart_filepath,
            SELL_RULES_CHART_FILEPATH_KEY: chart_paths_bundle.sell_rules_chart_filepath,
            ACCOUNT_VALUE_BAR_CHART_FILEPATH: chart_paths_bundle.account_value_bar_chart_filepath,
            POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY: chart_paths_bundle.positions_duration_bar_chart_filepath,
            POSITIONS_PROFIT_LOSS_BAR_CHART_FILEPATH_KEY: chart_paths_bundle.positions_profit_loss_bar_chart_filepath,
            POSITIONS_PROFIT_LOSS_HISTOGRAM_CHART_FILEPATH_KEY: chart_paths_bundle.positions_profit_loss_histogram_chart_filepath  # noqa
        }

    def __multi_pre_process(self, symbols: List[str], progress_observer: ProgressObserver) -> float:
        """Pre-process tasks for a multi-sim."""
        log.debug('Running multi simulation pre-process...')
        self.__running_multiple = True

        FSController.remove_temp_figures()

        # reset the multiple simulation archived symbols to clear any data from previous multiple simulations
        self.__multiple_simulation_position_archive = []

        return self.__calculate_multi_progress_bar_increment(symbols, progress_observer)

    def __multi_post_process(self, symbols: List[str], results: List[dict], start_time: float, results_depth: int,
                             save_option: int, progress_observer: ProgressObserver) -> dict:
        """Post-process tasks for a multi-sim."""
        log.info('Running multi simulation post-process...')
        self.gui_status_log.info('Starting analytics...')
        self.__running_multiple = False
        # save the results in case the user wants to write them to file
        self.__stored_results = results

        # initiate an analyzer with the positions data
        analyzer = PositionsAnalyzer(self.__multiple_simulation_position_archive)

        chart_paths_bundle = self.__create_multi_charts(results, results_depth, save_option)

        end_time = perf_counter()
        elapsed_time = round(end_time - start_time, 4)

        self.gui_status_log.info('Analytics complete \u2705')

        if progress_observer:
            progress_observer.set_analytics_complete()

        return {
            STRATEGY_KEY: self.__algorithm.strategy_filename,
            SYMBOLS_KEY: symbols,
            SIMULATION_START_TIMESTAMP_KEY: self.__algorithm.strategy[START_KEY],
            SIMULATION_END_TIMESTAMP_KEY: self.__algorithm.strategy[END_KEY],
            INITIAL_ACCOUNT_VALUE_KEY: self.__account.get_initial_balance(),
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
            OVERVIEW_CHART_FILEPATH_KEY: chart_paths_bundle.overview_chart_filepath,
            BUY_RULES_CHART_FILEPATH_KEY: chart_paths_bundle.buy_rules_chart_filepath,
            SELL_RULES_CHART_FILEPATH_KEY: chart_paths_bundle.sell_rules_chart_filepath,
            POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY: chart_paths_bundle.positions_duration_bar_chart_filepath,
            POSITIONS_PROFIT_LOSS_BAR_CHART_FILEPATH_KEY: chart_paths_bundle.positions_profit_loss_bar_chart_filepath,
            POSITIONS_PROFIT_LOSS_HISTOGRAM_CHART_FILEPATH_KEY: chart_paths_bundle.positions_profit_loss_histogram_chart_filepath  # noqa
        }

    def __reset_singular_attributes(self):
        """Clear singular simulation stored data."""
        self.__account.reset()
        self.__single_simulation_position_archive = []
        self.__account_value_archive = []

    def __create_position(self, current_day_index: int, rule: str) -> Position:
        """Creates a position and updates the account.

        Notes:
            The assumption is that the user wants to use full buying power (for now).
        """
        log.info('Creating the position...')

        buy_price = self.__data_manager.get_data_point(self.__data_manager.CLOSE, current_day_index)
        share_count = float(math.floor(self.__account.get_balance() / buy_price))

        new_position = Position(buy_price, share_count, current_day_index, rule)

        log.info('Position created successfully')

        self.__account.withdraw(round(buy_price * share_count, 3))

        return new_position

    def __liquidate_position(self, position: Position, current_day_index: int, rule: str):
        """Closes the position and updates the account."""
        log.info('Closing the position...')

        sell_price = float(self.__data_manager.get_data_point(self.__data_manager.CLOSE, current_day_index))

        position.close_position(sell_price, current_day_index, rule)

        if self.__is_stock_split(position, sell_price):
            self.gui_status_log.warning(f'Stock split avoided at day: {current_day_index}')
            log.info('Position excluded due to stock split!')
            # deposit the initial investment amount (undoing the withdrawal)
            self.__account.deposit(position.get_buy_price() * position.get_share_count())
            # skip adding the position to the list
            return

        self.__single_simulation_position_archive.append(position)

        log.info('Position closed successfully')

        self.__account.deposit(round(sell_price * position.get_share_count(), 3))

    def __add_positions_to_data(self) -> None:
        """Add the position data to the simulation data.

        Notes:
            Not every row in the data will have a value. To fix this we declare a list of None values the size of the
            simulation. Then we insert the data matching the index to the row. The indexes without a value are left as
            None. Then we can send the list to the df.
        """
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

    def __add_account_values_to_data(self) -> None:
        """Add the account value values to the simulation data.

        Notes:
            Unlike __add_positions_to_data(), the account value archive list has values for every day of the simulation.
            Because of this, we do not need to normalize and can cut straight to adding the values to the df.
        """
        # initialize the lists to the length of the simulation (with None values)
        account_values_list = [None for _ in range(self.__data_manager.get_data_length())]

        # calculate the start index of the archive relative to the simulation
        start_index = self.__data_manager.get_data_length() - len(self.__account_value_archive)

        # replace None values with account values
        j = 0
        for i in range(start_index, self.__data_manager.get_data_length()):
            account_values_list[i] = self.__account_value_archive[j]
            j += 1

        self.__data_manager.add_column('Account Value', account_values_list)

    def __create_singular_charts(self, symbol: str, chopped_temp_df: DataFrame, results_depth: int, save_option: int,
                                 show_volume: bool) -> SingularSimulationChartPathBundle:
        """Creates single-sim charts by saving them to files and returns their filepaths."""
        overview_chart_filepath = ''
        buy_rules_chart_filepath = ''
        sell_rules_chart_filepath = ''
        account_value_bar_chart_filepath = ''
        positions_duration_bar_chart_filepath = ''
        positions_profit_loss_bar_chart_filepath = ''
        positions_profit_loss_histogram_chart_filepath = ''

        if not self.__running_multiple:
            if results_depth == self.CHARTS_AND_DATA:
                # faster to do it synchronously for singular
                self.gui_status_log.info('Building overview chart...')
                overview_chart_filepath = (
                    SingularChartingEngine.build_indicator_chart(chopped_temp_df, symbol,
                                                                 [*self.__available_indicators.values()],
                                                                 show_volume, save_option))

                self.gui_status_log.info('Building buy rules bar chart...')
                buy_rules_chart_filepath = (
                    ChartingEngine.build_rules_bar_chart(self.__single_simulation_position_archive, BUY_SIDE, symbol,
                                                         save_option))

                self.gui_status_log.info('Building sell rules bar chart...')
                sell_rules_chart_filepath = (
                    ChartingEngine.build_rules_bar_chart(self.__single_simulation_position_archive, SELL_SIDE, symbol,
                                                         save_option))

                self.gui_status_log.info('Building account value line chart...')
                account_value_bar_chart_filepath = (
                    SingularChartingEngine.build_account_value_line_chart(chopped_temp_df, symbol, save_option))

                self.gui_status_log.info('Building positions duration bar chart...')
                positions_duration_bar_chart_filepath = (
                    ChartingEngine.build_positions_duration_bar_chart(self.__single_simulation_position_archive, symbol,
                                                                      save_option))

                self.gui_status_log.info('Building positions profit loss bar chart...')
                positions_profit_loss_bar_chart_filepath = (
                    SingularChartingEngine.build_positions_profit_loss_bar_chart(
                        self.__single_simulation_position_archive, symbol, save_option))

                self.gui_status_log.info('Building positions profit loss histogram chart...')
                positions_profit_loss_histogram_chart_filepath = (
                    ChartingEngine.build_positions_profit_loss_percent_histogram_chart(
                        self.__single_simulation_position_archive, self.__algorithm.strategy_filename, symbol,
                        save_option))

        return SingularSimulationChartPathBundle(overview_chart_filepath,
                                                 buy_rules_chart_filepath,
                                                 sell_rules_chart_filepath,
                                                 account_value_bar_chart_filepath,
                                                 positions_duration_bar_chart_filepath,
                                                 positions_profit_loss_bar_chart_filepath,
                                                 positions_profit_loss_histogram_chart_filepath)

    def __create_multi_charts(self, results, results_depth: int, save_option: int) -> MultiSimulationChartPathBundle:
        """Creates multi-sim charts by saving them to files and returns their filepaths."""
        overview_chart_filepath = ''
        buy_rules_chart_filepath = ''
        sell_rules_chart_filepath = ''
        positions_duration_bar_chart_filepath = ''
        positions_profit_loss_bar_chart_filepath = ''
        positions_profit_loss_histogram_chart_filepath = ''
        if results_depth == self.CHARTS_AND_DATA:
            with ProcessPoolExecutor() as executor:
                self.gui_status_log.info('Building overview chart...')
                future1 = executor.submit(MultiChartingEngine.build_overview_chart, results,
                                          self.__account.get_initial_balance(), save_option)

                self.gui_status_log.info('Building buy rules bar chart...')
                future2 = executor.submit(ChartingEngine.build_rules_bar_chart,
                                          self.__single_simulation_position_archive, BUY_SIDE, None, save_option)

                self.gui_status_log.info('Building sell rules bar chart...')
                future3 = executor.submit(ChartingEngine.build_rules_bar_chart,
                                          self.__single_simulation_position_archive, SELL_SIDE, None, save_option)

                self.gui_status_log.info('Building positions duration bar chart...')
                future4 = executor.submit(ChartingEngine.build_positions_duration_bar_chart,
                                          self.__single_simulation_position_archive, None, save_option)

                self.gui_status_log.info('Building positions profit loss bar chart...')
                future5 = executor.submit(ChartingEngine.build_positions_profit_loss_bar_chart,
                                          self.__single_simulation_position_archive, None, save_option)

                self.gui_status_log.info('Building positions profit loss histogram chart...')
                future6 = executor.submit(ChartingEngine.build_positions_profit_loss_percent_histogram_chart,
                                          self.__single_simulation_position_archive, self.__algorithm.strategy_filename,
                                          None, save_option)

                overview_chart_filepath = future1.result()
                buy_rules_chart_filepath = future2.result()
                sell_rules_chart_filepath = future3.result()
                positions_duration_bar_chart_filepath = future4.result()
                positions_profit_loss_bar_chart_filepath = future5.result()
                positions_profit_loss_histogram_chart_filepath = future6.result()

        return MultiSimulationChartPathBundle(overview_chart_filepath,
                                              buy_rules_chart_filepath,
                                              sell_rules_chart_filepath,
                                              positions_duration_bar_chart_filepath,
                                              positions_profit_loss_bar_chart_filepath,
                                              positions_profit_loss_histogram_chart_filepath)

    def __calculate_progress_bar_increment(self, progress_observer: ProgressObserver,
                                           sim_window_start_day: int) -> float:
        """Calculate the single-sim progress bar increment per day."""
        increment = 1.0  # default value
        if progress_observer is not None:
            increment = round(100.0 / (self.__data_manager.get_data_length() - sim_window_start_day), 2)
        return increment

    @staticmethod
    def __calculate_multi_progress_bar_increment(symbols: List[str],
                                                 progress_observer: ProgressObserver) -> float:
        """Calculate the multi-sim progress bar increment percentage per day."""
        increment = 1.0  # default value
        if progress_observer is not None:
            increment = 100.0 / float(len(symbols))
        return increment

    @staticmethod
    def __calculate_simulation_window(start_date_unix: int, end_date_unix: int, augmented_start_date_unix: int,
                                      data_manager: DataManager) -> tuple:
        """Calculate simulation window dimensions."""
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
    def __print_header(symbol: str) -> None:
        print('======= Simulation Start =======')
        print(f'Running simulation on {symbol}...')
        print('================================')

    @staticmethod
    def __log_details(filename: str, symbol: str, start_date: str, end_date: str, window_size: int, tradable_days: int,
                      balance: float) -> None:
        log.info('==== Simulation Details =====')
        log.info(f'Strategy        : {filename}')
        log.info(f'Symbol          : {symbol}')
        log.info(f'Start Date      : {start_date}')
        log.info(f'End Date        : {end_date}')
        log.info(f'Window Size     : {window_size}')
        log.info(f'Trade-able Days : {tradable_days}')
        log.info(f'Account Value   : $ {balance}')
        log.info('=============================')

    @staticmethod
    def __log_results(elapsed_time: float, analyzer: PositionsAnalyzer, balance: float) -> None:
        log.info('====== Simulation Results ======')
        log.info(f'Elapsed Time  : {elapsed_time} seconds')
        log.info(f'Trades Made   : {analyzer.total_trades()}')
        log.info(f'Effectiveness : {analyzer.effectiveness()} %')
        log.info(f'Total P/L     : $ {analyzer.total_profit_loss()}')
        log.info(f'Average P/L   : $ {analyzer.average_profit_loss()}')
        log.info(f'Median P/L    : $ {analyzer.median_profit_loss()}')
        log.info(f'Stddev P/L    : $ {analyzer.standard_profit_loss_deviation()}')
        log.info(f'Account Value : $ {balance}')
        log.info('================================')

    @staticmethod
    def __print_singular_results(elapsed_time: float, analyzer: PositionsAnalyzer, balance: float) -> None:
        print('====== Simulation Results ======')
        print(f'Elapsed Time  : {elapsed_time} seconds')
        print(f'Trades Made   : {analyzer.total_trades()}')
        print(f'Effectiveness : {analyzer.effectiveness()} %')
        print(f'Total P/L     : $ {analyzer.total_profit_loss()}')
        print(f'Average P/L   : $ {analyzer.average_profit_loss()}')
        print(f'Median P/L    : $ {analyzer.median_profit_loss()}')
        print(f'Stddev P/L    : $ {analyzer.standard_profit_loss_deviation()}')
        print(f'Account Value : $ {balance}')
        print('================================')

    @staticmethod
    def __unix_to_string(timestamp: int, date_format: str = '%m-%d-%Y') -> str:
        """Convert a unix date to a string of custom format."""
        return datetime.fromtimestamp(timestamp).strftime(date_format)
