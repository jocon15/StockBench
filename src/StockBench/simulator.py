import re
import time
import math
import logging
from tqdm import tqdm
from datetime import datetime
from .broker.broker_api import *
from .charting.charting_api import *
from .accounting.user_account import *
from .indicators.indicators_api import *
from .position.position_obj import *
from .analysis.analysis_api import *

SECONDS_PER_DAY = 86400
DEFAULT_RSI_LENGTH = 14

log = logging.getLogger()  # root


# ------------ - Additional days needed for accurate indicators at simulation start (algorithm defined)
# |   OHLC   |
# |   OHLC   |
# ------------ - Start of the simulation (user defined)
# |   OHLC   |
# |   OHLC   |
# |   OHLC   |
# |   OHLC   |
# |   OHLC   |
# |   OHLC   |
# ------------ - End of the simulation (user defined)


class Simulator:
    def __init__(self, balance: float):
        self.__account = UserAccount(balance)
        self.__broker_API = BrokerAPI()
        self.__charting_API = ChartingAPI()
        self.__indicators_API = Indicators()  # gets constructed once we have the data
        self.__analyzer_API = None  # gets constructed once we have the data

        self.__strategy = None
        self.__start_date_unix = None
        self.__end_date_unix = None
        self.__augmented_start_date_unix = None

        self.__df = None
        self.__symbol = None

        self.__buy_list = list()
        self.__sell_list = list()

        self.__position_archive = list()

        self.__reporting_on = False
        self.__charting_on = False

    def enable_logging(self):
        """Enable user logging."""
        # set the logging level to info
        log.setLevel(logging.INFO)

        # build the filepath
        user_logging_filepath = f'logs\\RunLog_{self.datetime_nonce_string()}'

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

    def enable_developer_logging(self, _level=2):
        """Enable developer logging."""
        # set the logging level
        if _level == 1:
            log.setLevel(logging.DEBUG)
            # build the formatter
            developer_logging_formatter = logging.Formatter('%(funcName)s:%(lineno)d|%(levelname)s|%(message)s')
        elif _level == 3:
            log.setLevel(logging.WARNING)
            # build the formatter
            developer_logging_formatter = logging.Formatter('%(lineno)d|%(levelname)s|%(message)s')
        elif _level == 4:
            log.setLevel(logging.ERROR)
            # build the formatter
            developer_logging_formatter = logging.Formatter('%(lineno)d|%(levelname)s|%(message)s')
        elif _level == 5:
            log.setLevel(logging.CRITICAL)
            # build the formatter
            developer_logging_formatter = logging.Formatter('%(lineno)d|%(levelname)s|%(message)s')
        else:
            log.setLevel(logging.INFO)
            # build the formatter
            developer_logging_formatter = logging.Formatter('%(lineno)d|%(levelname)s|%(message)s')

        # build the filepath
        developer_logging_filepath = f'dev\\DevLog_{self.datetime_nonce_string()}'

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

    def enable_charting(self):
        """Enable charting."""
        self.__charting_on = True

    @staticmethod
    def datetime_nonce_string() -> str:
        """Convert current date and time to string."""
        return datetime.now().strftime("%m_%d_%Y__%H_%M_%S")

    @staticmethod
    def unix_to_string(_unix_date, _format='%m-%d-%Y') -> str:
        return datetime.utcfromtimestamp(_unix_date).strftime(_format)

    def load_strategy(self, strategy: dict):
        """Load a strategy.

         Args:
             strategy (dict): The strategy as a dictionary.
         """
        self.__strategy = strategy

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

    @staticmethod
    def __error_check_timestamps(_start, _end):
        """Simple check that the timestamps are valid."""
        if _start > _end:
            log.critical('Start timestamp must be before end timestamp')
            raise Exception('Start timestamp must be before end timestamp')
        if _start > int(time.time()):
            log.critical('Start timestamp must not be in the future')
            raise Exception('Start timestamp must not be in the future')

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
                    self.__add_RSI(num)
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
        self.__augmented_start_date_unix = self.__start_date_unix - (additional_days * SECONDS_PER_DAY)

    def __parse_strategy_rules(self):
        """Parse the strategy for relevant information needed to make the API request."""
        log.debug('Parsing strategy for indicators and rules...')
        additional_days = 0

        # build a list of sub keys from the buy and sell sections
        keys = list()
        if 'buy' in self.__strategy.keys():
            for key in self.__strategy['buy'].keys():
                keys.append(key)
        if 'sell' in self.__strategy.keys():
            for key in self.__strategy['sell'].keys():
                keys.append(key)

        # buy keys
        for key in self.__strategy['buy'].keys():
            if 'RSI' in key:
                # ======== key based =========
                nums = re.findall(r'\d+', key)
                if len(nums) == 1:
                    num = int(nums[0])
                    # add the RSI data to the df
                    self.__add_RSI(num)
                else:
                    # add the RSI data to the df
                    self.__add_RSI(DEFAULT_RSI_LENGTH)
                # ======== value based (rsi limit)=========
                _value = self.__strategy['buy'][key]
                _nums = re.findall(r'\d+', _value)
                if len(_nums) == 1:
                    _trigger = float(_nums[0])
                    self.__add_lower_RSI(_trigger)
            elif 'SMA' in key:
                nums = re.findall(r'\d+', key)
                if len(nums) == 1:
                    num = int(nums[0])
                    # add the SMA data to the df
                    self.__add_SMA(num)
        # sell keys
        for key in self.__strategy['sell'].keys():
            if 'RSI' in key:
                # ======== key based =========
                nums = re.findall(r'\d+', key)
                if len(nums) == 1:
                    num = int(nums[0])
                    # add the RSI data to the df
                    self.__add_RSI(num)
                else:
                    # add the RSI data to the df
                    self.__add_RSI(DEFAULT_RSI_LENGTH)
                # ======== value based (rsi limit)=========
                _value = self.__strategy['sell'][key]
                _nums = re.findall(r'\d+', _value)
                if len(_nums) == 1:
                    _trigger = float(_nums[0])
                    self.__add_upper_RSI(_trigger)
            elif 'SMA' in key:
                nums = re.findall(r'\d+', key)
                if len(nums) == 1:
                    num = int(nums[0])
                    # add the SMA data to the df
                    self.__add_SMA(num)

    def __add_RSI(self, _length: int):
        """Pre-calculate the RSI values and add them to the df."""
        # get a list of close price values
        price_data = list()
        for i in range(len(self.__df['Close'])):
            price_data.append(self.__df['Close'][i])

        # calculate the RSI values from the indicator API
        rsi_values = self.__indicators_API.RSI(DEFAULT_RSI_LENGTH, price_data)

        # add the calculated values to the df
        self.__df['RSI'] = rsi_values

    def __add_upper_RSI(self, _trigger_value: float):
        """Add upper RSI trigger to the df."""
        self.__df['RSI_upper'] = _trigger_value

    def __add_lower_RSI(self, _trigger_value: float):
        """Add lower RSI trigger to the df."""
        self.__df['RSI_lower'] = _trigger_value

    def __add_SMA(self, _length: int):
        """Pre-calculate the SMA values and add them to the df."""
        # get a list of close price values
        column_title = f'SMA{_length}'

        # if we already have SMA values in the df, we don't need to add them again
        # so just return
        for (col_name, col_vals) in self.__df.iteritems():
            if column_title in col_name:
                return

        # get a list of price values in the form of a list
        price_data = list()
        for i in range(len(self.__df['Close'])):
            price_data.append(self.__df['Close'][i])

        # calculate the SMA values from the indicator API
        sma_values = self.__indicators_API.SMA(_length, price_data)

        # add the calculated values to the df
        self.__df[column_title] = sma_values

    def __add_buys_sells(self):
        """Adds the buy and sell lists to the DataFrame."""
        self.__df['Buy'] = self.__buy_list
        self.__df['Sell'] = self.__sell_list

    def __create_position(self, _current_day_index: int) -> Position:
        """Creates a position and updates the account.

        Args:
            _current_day_index (int): The index of the current day

        return:
            Position: The created Position object.

        Notes:
            The assumption is that the user wants to use full buying power (for now)
        """
        log.info('Creating the position...')

        # add the buying price to the DataFrame
        _buy_price = self.__df['Close'][_current_day_index]

        # calculate the withdrawal amount (nearest whole share - floor direction)
        share_count = float(math.floor(self.__account.get_balance() / _buy_price))
        withdraw_amount = round(_buy_price * share_count, 3)

        # withdraw the money from the account
        self.__account.withdraw(withdraw_amount)

        log.info('Position created successfully')

        # build and return the new position
        return Position(_buy_price, share_count)

    def __liquidate_position(self, _position: Position, _current_day_index: int):
        """Closes the position and updates the account.

        Args:
            _position (Position): The position to close.
            _current_day_index (int): The index of the current day
        """
        log.info('Closing the position...')
        # close the position
        _position.close_position(self.__df['Close'][_current_day_index])

        # add the closing price to the DataFrame
        _sell_price = float(self.__df['Close'][_current_day_index])

        # add the position to the archive
        self.__position_archive.append(_position)

        # calculate the deposit amount
        deposit_amount = round(_position.get_sell_price() * _position.get_share_count(), 3)

        log.info('Position closed successfully')

        # deposit the value of the position to the account
        self.__account.deposit(deposit_amount)

    def run(self, symbol: str):
        """Run a simulation on an asset."""

        # ===================== Buying ==========================
        def handle_or_buy_triggers() -> tuple:
            """Abstraction for sorting the buy triggers with OR logic."""
            _position = None
            trigger_hit = False

            # check for all types of triggers
            if 'RSI' in key:
                trigger_hit = check_rsi_buy_trigger(key, self.__strategy['buy'][key])
            if 'SMA' in key:
                trigger_hit = check_sma_buy_trigger(key, self.__strategy['buy'][key])
            if key == 'color':
                trigger_hit = check_candle_colors_buy_trigger(self.__strategy['buy'][key])

            if trigger_hit:
                # create the position
                _position = self.__create_position(current_day_index)
                insert_buy()
                return _position, False

            # trigger was not hit
            return _position, True

        def handle_and_buy_triggers() -> tuple:
            """ Abstraction for sorting the buy triggers with AND logic

            Notes:
                 This is an AND comparison so all operands need to evaluate to true
            """
            _position = None
            for inner_key in self.__strategy['buy'][key].keys():
                # reset trigger indicator
                trigger_hit = False
                # check for all types of triggers
                if 'RSI' in key:
                    trigger_hit = check_rsi_buy_trigger(key, self.__strategy['buy'][key][inner_key])
                if 'SMA' in key:
                    trigger_hit = check_sma_buy_trigger(key, self.__strategy['buy'][key][inner_key])
                if key == 'color':
                    trigger_hit = check_candle_colors_buy_trigger(self.__strategy['buy'][key][inner_key])
                if not trigger_hit:
                    # not all triggers were hit
                    return _position, True
            # all triggers were hit

            # create the position
            _position = self.__create_position(current_day_index)
            insert_buy()
            return _position, False

        def check_rsi_buy_trigger(_key, _value) -> bool:
            """Abstracted logic for RSI buy signals.

            Args:
                _key (str): The key value of the trigger.
                _value (str): The value of the trigger.

            return:
                bool: True if the trigger was hit.

            Notes:
                This functions is internal (fxn inside fxn) which means everything in the outer
                function run() is global here
            """
            log.debug('Checking RSI buy triggers...')

            # find the value of the RSI else default
            _num = DEFAULT_RSI_LENGTH
            _nums = re.findall(r'\d+', _key)
            if len(_nums) == 1:
                _num = float(_nums[0])

            # get the RSI value for current day
            # old way where we calculate it on the spot (deprecated)
            # rsi = self.__indicators_API.RSI(_num, current_day_index)
            # new way where we just pull the pre-calculated value from the col in the df
            rsi = self.__df['RSI'][current_day_index]

            # check that the value from {key: value} has a number in it
            # this is the trigger value
            _nums = re.findall(r'\d+', _value)
            if len(_nums) == 1:
                _trigger = float(_nums[0])
            else:
                log.warning('Found invalid format RSI (invalid number found in trigger value)')
                print('Found invalid format RSI (invalid number found in trigger value)')
                # if no trigger value available, exit
                return False

            # trigger checks
            if '<=' in _value:
                if rsi <= _trigger:
                    log.info(f"RSI '<=' trigger hit!")
                    return True
            elif '>=' in _value:
                if rsi >= _trigger:
                    log.info(f"RSI '>=' trigger hit!")
                    return True
            elif '<' in _value:
                if rsi < _trigger:
                    log.info(f"RSI '<' trigger hit!")
                    return True
            elif '>' in _value:
                if rsi > _trigger:
                    log.info(f"RSI '>' trigger hit!")
                    return True
            elif '=' in _value:
                if rsi == _trigger:
                    log.info(f"RSI '==' trigger hit!")
                    return True

            log.debug('All RSI triggers checked')

            # catch all case if nothing was hit (which is ok!)
            # No position and buying is still enabled
            return False

        def check_sma_buy_trigger(_key, _value) -> bool:
            """Abstracted logic for SMA buy signals.

            Args:
                _key (str): The key value of the trigger.
                _value (str): The value of the trigger.

            return:
                bool: True if the trigger was hit.

            Notes:
                This functions is internal (fxn inside fxn) which means everything in the outer
                function run() is global here
            """
            log.debug('Checking SMA buy triggers...')

            # find the SMA length, else exit
            _nums = re.findall(r'\d+', _key)
            # since we have no default SMA, there must be a value provided, else exit
            if len(_nums) == 1:
                _num = int(_nums[0])

                # get the sma value for the current day
                # old way where we calculate it on the spot (deprecated)
                # sma = self.__indicators_API.SMA(_num, current_day_index)
                # new way where we just pull the pre-calculated value from the col in the df
                title = f'SMA{_num}'
                sma = self.__df[title][current_day_index]

                # check that the value from {key: value} has a number in it
                # this is the trigger value
                _nums = re.findall(r'\d+', _value)
                if len(_nums) == 1:
                    _trigger = float(_nums[0])
                else:
                    print('Found invalid format SMA (invalid number found in trigger value)')
                    # if no trigger value available, exit
                    return False

                # trigger checks
                if '<=' in _value:
                    if sma <= _trigger:
                        log.info(f"SMA '<=' trigger hit!")
                        return True
                elif '>=' in _value:
                    if sma >= _trigger:
                        log.info(f"SMA '>=' trigger hit!")
                        return True
                elif '<' in _value:
                    if sma < _trigger:
                        log.info(f"SMA '<' trigger hit!")
                        return True
                elif '>' in _value:
                    if sma > _trigger:
                        log.info(f"SMA '>' trigger hit!")
                        return True
                elif '=' in _value:
                    if sma == _trigger:
                        log.info(f"SMA '==' trigger hit!")
                        return True

                log.debug('All SMA triggers checked')

                # catch all case if nothing was hit (which is ok!)
                return False

            log.warning(f'Warning: {key} is in incorrect format and will be ignored')
            print(f'Warning: {key} is in incorrect format and will be ignored')
            return False

        def check_candle_colors_buy_trigger(_value) -> bool:
            """Abstracted logic for candle stick buy signals.

            Args:
                _value (dict): The value of the trigger.

            return:
                bool: True if the trigger was hit.

            Notes:
                This functions is internal (fxn inside fxn) which means everything in the outer
                function run() is global here.
            """
            log.debug('Checking candle stick buy triggers...')

            # find out how many keys there are (_value is a dict)
            num_keys = len(_value)

            # these will both need to be in ascending order [today, yesterday...]
            trigger_colors = list()
            actual_colors = list()

            # build the trigger list
            for _key in sorted(_value.keys()):
                trigger_colors.append(_value[_key])

            # build the actual list
            for i in range(num_keys):
                actual_colors.append(self.__indicators_API.candle_color(current_day_index - i))

            # check for trigger
            if actual_colors == trigger_colors:
                log.info('Candle stick trigger hit!')
                return True

            log.debug('All candle stick triggers checked')

            # catch all case if nothing was hit (which is ok!)
            return False

        # ===================== Selling ===========================

        def handle_or_sell_triggers() -> tuple:
            """Abstraction for sorting the buy triggers with OR logic."""
            trigger_hit = False

            # check for all types of triggers
            if 'RSI' in key:
                trigger_hit = check_rsi_sell_trigger(key, self.__strategy['sell'][key])
            if 'SMA' in key:
                trigger_hit = check_sma_sell_trigger(key, self.__strategy['sell'][key])
            if key == 'stop_loss':
                trigger_hit = check_stop_loss_sell_trigger(self.__strategy['sell'][key])
            if key == 'stop_profit':
                trigger_hit = check_stop_profit_sell_trigger(self.__strategy['sell'][key])
            if key == 'color':
                trigger_hit = check_candle_colors_sell_trigger(self.__strategy['sell'][key])

            if trigger_hit:
                # create the position
                self.__liquidate_position(position, current_day_index)
                insert_sell()
                return None, True

            # trigger was not hit
            return position, False

        def handle_and_sell_triggers() -> tuple:
            """ Abstraction for sorting the sell triggers with AND logic

            Notes:
                 This is an AND comparison so all operands need to evaluate to true
            """
            for inner_key in self.__strategy['sell'][key].keys():
                # reset trigger indicator
                trigger_hit = False
                # check for all types of triggers
                if 'RSI' in key:
                    trigger_hit = check_rsi_sell_trigger(key, self.__strategy['sell'][key][inner_key])
                if 'SMA' in key:
                    trigger_hit = check_sma_sell_trigger(key, self.__strategy['sell'][key][inner_key])
                if key == 'stop_loss':
                    trigger_hit = check_stop_loss_sell_trigger(self.__strategy['sell'][key][inner_key])
                if key == 'stop_profit':
                    trigger_hit = check_stop_profit_sell_trigger(self.__strategy['sell'][key][inner_key])
                if key == 'color':
                    trigger_hit = check_candle_colors_sell_trigger(self.__strategy['sell'][key][inner_key])
                if not trigger_hit:
                    # not all triggers were hit
                    return position, False
            # all triggers were hit

            # liquidate the position
            self.__liquidate_position(position, current_day_index)
            insert_sell()
            return None, True

        def check_rsi_sell_trigger(_key, _value) -> bool:
            """Abstracted logic for RSI sell signals.

            Args:
                _key (str): The key value of the trigger.
                _value (str): The value of the trigger.

            return:
                bool: True if the trigger was hit.

            Notes:
                This functions is internal (fxn inside fxn) which means everything in the outer
                function run() is global here

            """
            log.debug('Checking RSI sell triggers...')

            # find the value of the RSI else default
            _num = DEFAULT_RSI_LENGTH
            _nums = re.findall(r'\d+', _key)
            if len(_nums) == 1:
                _num = float(_nums[0])

            # get the RSI value for current day
            # old way where we calculate it on the spot (deprecated)
            # rsi = self.__indicators_API.RSI(_num, current_day_index)
            # new way where we just pull the pre-calculated value from the col in the df
            rsi = self.__df['RSI'][current_day_index]

            # check that the value from {key: value} has a number in it
            # this is the trigger value
            _nums = re.findall(r'\d+', _value)
            if len(_nums) == 1:
                _trigger = float(_nums[0])
            else:
                print('Found invalid format RSI (invalid number found in trigger value)')
                # if no trigger value available, exit
                return False

            # trigger checks
            if '<=' in _value:
                if rsi <= _trigger:
                    log.info(f"RSI '<=' trigger hit!")
                    return True
            elif '>=' in _value:
                if rsi >= _trigger:
                    log.info(f"RSI '>=' trigger hit!")
                    return True
            elif '<' in _value:
                if rsi < _trigger:
                    log.info(f"RSI '<' trigger hit!")
                    return True
            elif '>' in _value:
                if rsi > _trigger:
                    log.info(f"RSI '>' trigger hit!")
                    return True
            elif '=' in _value:
                if rsi == _trigger:
                    log.info(f"RSI '==' trigger hit!")
                    return True

            log.debug('All RSI triggers checked')

            # catch all case if nothing was hit (which is ok!)
            # No position and buying is still enabled
            return False

        def check_sma_sell_trigger(_key, _value) -> bool:
            """Abstracted logic for RSI sell signals.

            Args:
                _key (str): The key value of the trigger.
                _value (str): The value of the trigger.

            return:
                bool: True if the trigger was hit.

            Notes:
                This functions is internal (fxn inside fxn) which means everything in the outer
                function run() is global here
            """
            log.debug('Checking SMA sell triggers...')

            # find the SMA length, else exit
            _nums = re.findall(r'\d+', _key)
            # since we have no default SMA, there must be a value provided, else exit
            if len(_nums) == 1:
                _num = int(_nums[0])

                # get the sma value for the current day
                # old way where we calculate it on the spot (deprecated)
                # sma = self.__indicators_API.SMA(_num, current_day_index)
                # new way where we just pull the pre-calculated value from the col in the df
                title = f'SMA{_num}'
                sma = self.__df[title][current_day_index]

                # check that the value from {key: value} has a number in it
                # this is the trigger value
                _nums = re.findall(r'\d+', _value)
                if len(_nums) == 1:
                    _trigger = float(_nums[0])
                else:
                    print('Found invalid format SMA (invalid number found in trigger value)')
                    # if no trigger value available, exit
                    return False

                # trigger checks
                if '<=' in _value:
                    if sma <= _trigger:
                        log.info(f"SMA '<=' trigger hit!")
                        return True
                elif '>=' in _value:
                    if sma >= _trigger:
                        log.info(f"SMA '>=' trigger hit!")
                        return True
                elif '<' in _value:
                    if sma < _trigger:
                        log.info(f"SMA '<' trigger hit!")
                        return True
                elif '>' in _value:
                    if sma > _trigger:
                        log.info(f"SMA '>' trigger hit!")
                        return True
                elif '=' in _value:
                    if sma == _trigger:
                        log.info(f"SMA '==' trigger hit!")
                        return True

                log.debug('All SMA triggers checked')

                # catch all case if nothing was hit (which is ok!)
                return False

            log.warning(f'Warning: {key} is in incorrect format and will be ignored')

            print(f'Warning: {key} is in incorrect format and will be ignored')
            return False

        def check_stop_profit_sell_trigger(_value) -> bool:
            """Abstracted logic for stop profit sell signals.

            Args:
                _value (str): The value of the trigger.

            return:
                bool: True if the trigger was hit.

            Notes:
                This functions is internal (fxn inside fxn) which means everything in the outer
                function run() is global here.
            """
            log.debug('Checking stop profit triggers...')

            # get the trigger from the strategy
            _trigger = float(_value)

            # get the profit/loss from the strategy
            p_l = position.profit_loss(self.__df['Close'][current_day_index])

            # check for profit
            if p_l > 0:
                # check for trigger
                if p_l >= _trigger:
                    log.info('Stop profit trigger hit!')
                    return True

            log.debug('Stop profit triggers checked')

            # catch all case if nothing was hit (which is ok!)
            return False

        def check_stop_loss_sell_trigger(_value) -> bool:
            """Abstracted logic for stop loss sell signals.

            Args:
                _value (str): The value of the trigger.

            return:
                bool: True if the trigger was hit.

            Notes:
                This functions is internal (fxn inside fxn) which means everything in the outer
                function run() is global here.
            """
            log.debug('Checking stop loss triggers...')

            # get the trigger from the strategy
            _trigger = float(_value)

            # get the profit/loss from the position
            p_l = position.profit_loss(self.__df['Close'][current_day_index])

            # check for a loss
            if p_l < 0:
                # check trigger
                if abs(p_l) >= abs(_trigger):
                    log.info('Stop loss trigger hit!')
                    return True

            log.debug('Stop loss triggers checked')

            # catch all case if nothing was hit (which is ok!)
            return False

        def check_candle_colors_sell_trigger(_value) -> bool:
            """Abstracted logic for stop loss sell signals.

            Args:
                _value (dict): The value of the trigger.

            return:
                bool: True if the trigger was hit.

            Notes:
                This functions is internal (fxn inside fxn) which means everything in the outer
                function run() is global here.
            """
            log.debug('Checking candle stick sell triggers')

            # find out how many keys there are
            num_keys = len(_value)

            # these will both need to be in ascending order [today, yesterday...]
            trigger_colors = list()
            actual_colors = list()

            # build the trigger list
            for _key in sorted(_value.keys()):
                trigger_colors.append(_value[_key])

            # build the actual list
            for i in range(num_keys):
                actual_colors.append(self.__indicators_API.candle_color(current_day_index - i))

            # check for trigger
            if actual_colors == trigger_colors:
                log.info('Candle stick trigger hit!')
                return True

            log.debug('All candle stick triggers checked')

            # catch all case if nothing was hit (which is ok!)
            return False

        def insert_buy():
            """Abstraction for adding a buy to the buy list."""
            self.__buy_list[current_day_index] = self.__df['Close'][current_day_index]

        def insert_sell():
            """Abstraction for adding a sell to the sell list."""
            self.__sell_list[current_day_index] = self.__df['Close'][current_day_index]

        # set the objects symbol to the passed value, so we can use it everywhere
        log.info(f'Setting up simulation for symbol: {symbol}...')
        self.__symbol = symbol.upper()

        # check the strategy for errors
        self.__error_check_strategy()

        # parse the strategy for timestamps, so we know what the user wants
        self.__parse_strategy_timestamps()

        # get the data from the servers
        self.__df = self.__broker_API.get_daily_data(self.__symbol,
                                                     self.__augmented_start_date_unix,
                                                     self.__end_date_unix)

        # parse the strategy for rules
        self.__parse_strategy_rules()

        # give the indicators API the data
        self.__indicators_API.add_data(self.__df)

        # calculate window lengths
        total_days = int((self.__end_date_unix - self.__augmented_start_date_unix) / SECONDS_PER_DAY)
        days_in_focus = int((self.__end_date_unix - self.__start_date_unix) / SECONDS_PER_DAY)
        focus_start_day = total_days - days_in_focus
        trade_able_days = len(self.__df["Close"]) - focus_start_day

        buy_mode = True
        position = None

        # initialize the lists to the correct size (values to None)
        self.__buy_list = [None for _ in range(len(self.__df['Close']))]
        self.__sell_list = [None for _ in range(len(self.__df['Close']))]

        log.info(f'Setup for symbol: {self.__symbol} complete')

        log.info('==== Simulation Details =====')
        log.info(f'Symbol          : {self.__symbol}')
        log.info(f'Start Date      : {self.unix_to_string(self.__start_date_unix)}')
        log.info(f'End Date        : {self.unix_to_string(self.__end_date_unix)}')
        log.info(f'Window Size     : {days_in_focus}')
        log.info(f'Trade-able Days : {trade_able_days}')
        log.info(f'Account Value   : {self.__account.get_balance()}')
        log.info('=============================')

        log.info(f'Beginning simulation...')

        # ===================== Simulation Loop ======================
        for current_day_index in tqdm(range(focus_start_day, len(self.__df['Close']))):
            # we loop from the focus start day (ex. 200)
            # to the total amount of days in the set (ex. 400)
            # the day_index represents the index of the current day in the
            # data set, so if we need something like SMA200 we just get all
            # the days from now to now-200
            # we can have an indicator package like viper that takes a df
            # a start and an end day and calculate the SMA X

            # --- debug ----
            # os.system('cls')
            # print(f'Current Day index: {current_day_index}')
            # --- debug ----

            log.debug(f'Current day index: {current_day_index}')

            if buy_mode:
                buy_keys = self.__strategy['buy'].keys()
                for key in buy_keys:
                    if 'and' in key:
                        # handle and triggers
                        position, buy_mode = handle_and_buy_triggers()
                    else:
                        # handle or triggers
                        position, buy_mode = handle_or_buy_triggers()
                    if not buy_mode:
                        break
            else:
                # sell mode
                sell_keys = self.__strategy['sell'].keys()
                for key in sell_keys:
                    if 'and' in key:
                        # handle and triggers
                        position, buy_mode = handle_and_sell_triggers()
                    else:
                        # handle or triggers
                        position, buy_mode = handle_or_sell_triggers()
                if buy_mode:
                    break
                if current_day_index == (len(self.__df['Close']) - 1):
                    # the position is still open at the end of the simulation
                    log.info('Position closed due to end of simulation reached')
                    self.__liquidate_position(position, self.__df['Close'][current_day_index])
                    insert_sell()
                    break

        # add the buys and sells to the df
        self.__add_buys_sells()

        # chop the dataframe and reset index
        self.__df.drop(index=range(0, focus_start_day), inplace=True)
        self.__df.reset_index(inplace=True)

        log.info('Simulation complete!')

        # initiate the analyzer with the positions data
        self.__analyzer_API = SimulationAnalyzer(self.__position_archive)

        log.info('====== Simulation Results ======')
        log.info(f'Trades made   : {len(self.__position_archive)}')
        log.info(f'Total P/L     : {self.__analyzer_API.total_pl()}')
        log.info(f'Avg. P/L      : {self.__analyzer_API.avg_pl()}')
        log.info(f'Effectiveness : {self.__analyzer_API.effectiveness()}')
        log.info(f'Account Value : {self.__account.get_balance()}')
        log.info('================================')

        print('====== Simulation Results ======')
        print(f'Trades made   : {len(self.__position_archive)}')
        print(f'Total P/L     : {self.__analyzer_API.total_pl()}')
        print(f'Avg. P/L      : {self.__analyzer_API.avg_pl()}')
        print(f'Effectiveness : {self.__analyzer_API.effectiveness()}')
        print(f'Account Value : {self.__account.get_balance()}')
        print('================================')

        # any report building goes here!
        # FIXME: Report building
        #   - I like being able to see the dataframe
        #   - We could export the df to excel
        #       - the df already looks like an excel sheet

        if self.__charting_on:
            self.__charting_API.chart(self.__df, self.__symbol)
