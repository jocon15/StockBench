import re
import time
from .broker.broker_api import *
from .charting.charting_api import *
from .accounting.user_account import *
from .indicators.indicators_api import *
from .position.position_obj import *

SECONDS_PER_DAY = 86400
DEFAULT_RSI_LENGTH = 14


class Simulator:
    def __init__(self, balance: float):
        self.__account = UserAccount(balance)
        self.__broker_API = BrokerAPI()
        self.__charting_API = ChartingAPI()
        self.__indicators_API = None  # gets constructed once we have the data

        self.__strategy = None
        self.__start_date_unix = None
        self.__end_date_unix = None
        self.__augmented_start_date_unix = None

        self.__symbol = None

        self.__buys = list()
        self.__sells = list()

    def load_strategy(self, strategy: dict):
        if not strategy:
            raise Exception('Strategy cannot be empty')
        self.__strategy = strategy

    def __error_check_strategy(self):
        if not self.__strategy:
            raise Exception('No strategy uploaded')

        if 'start' not in self.__strategy.keys():
            raise Exception("Strategy missing 'start' key")

        if 'end' not in self.__strategy.keys():
            raise Exception("Strategy missing 'end' key")

        if 'buy' not in self.__strategy.keys():
            raise Exception("Strategy missing 'buy' key")

        if 'sell' not in self.__strategy.keys():
            raise Exception("Strategy missing 'sell' key")

    @staticmethod
    def __error_check_timestamps(_start, _end):
        """Simple check that the timestamps are valid."""
        if _start > _end:
            raise Exception('Start timestamp must be before end timestamp')
        if _start > int(time.time()):
            raise Exception('Start timestamp must not be in the future')

    def __parse_strategy(self):
        """Parse the strategy for relevant information needed to make the API request."""
        additional_days = 0

        # build a list of sub keys from the buy and sell sections
        keys = list()
        if 'start' in self.__strategy.keys():
            self.__start_date_unix = int(self.__strategy['start'])
        if 'end' in self.__strategy.keys():
            self.__end_date_unix = int(self.__strategy['end'])

        if 'buy' in self.__strategy.keys():
            for key in self.__strategy['buy'].keys():
                keys.append(key)
        if 'sell' in self.__strategy.keys():
            for key in self.__strategy['sell'].keys():
                keys.append(key)

        for key in keys:
            if 'RSI' in key:
                if additional_days < 14:
                    additional_days = 14
            elif 'SMA' in key:
                nums = re.findall(r'\d+', key)
                if len(nums) == 1:
                    num = int(nums[0])
                    if additional_days < num:
                        additional_days = num
            elif 'color' in key:
                try:
                    num = len(self.__strategy['buy']['color'])
                    if type(num) != dict:
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

    def __create_position(self, _buy_price) -> Position:
        """Creates a position and updates the account.

        Args:
            _buy_price (float): The asset price that the position is purchased at.

        return:
            Position: The created Position object.

        Notes:
            The assumption is that the user wants to use full buying power (for now)
        """
        # add the buying price to the buy list
        self.__buys.append(_buy_price)

        # calculate the withdrawal amount
        share_count = round(self.__account.get_balance() / _buy_price, 3)
        withdraw_amount = round(_buy_price * share_count, 3)

        # withdraw the money from the account
        self.__account.withdraw(withdraw_amount)

        # build and return the new position
        return Position(_buy_price, share_count)

    def __liquidate_position(self, _position: Position, _sell_price: float):
        """Closes the position and updates the account.

        Args:
            _position (Position): The position to close.
            _sell_price (float): The asset price that the position is sold at.
        """
        # close the position
        _position.close_position(_sell_price)

        # add the closing price to the sell list
        self.__sells.append(_sell_price)

        # calculate the deposit amount
        deposit_amount = round(_position.get_sell_price() * _position.get_share_count(), 3)

        # deposit the value of the position to the account
        self.__account.deposit(deposit_amount)

    def run(self, symbol: str):
        """"""
        # ===================== Buying ==========================
        # FIXME: If the script is buying, there is no position open
        #   - so why do we need to pass _position?
        #   - What if we want to have some sort of method where you could have multiple open trades?
        #   - Multiple trades gets very complex very quick, and it is hard to get the user to input
        #   - it in a way that is manageable by the code
        #   - IN THESE functions for buy, we don't need to pass in anything, we just need to return
        #   - the tuple
        def handle_RSI_buys() -> tuple:
            """Abstracted logic for RSI buy signals.

            return:
                tuple: The (Position, bool) tuple of the position created and the buying enabled signal

            Notes:
                This functions is internal (fxn inside fxn) which means everything in the outer
                function run() is global here
            """
            # get the unchecked trigger value from the strategy
            _value = self.__strategy['buy'][key]
            # find the value of the RSI else default
            _num = DEFAULT_RSI_LENGTH
            _nums = re.findall(r'\d+', key)
            if len(_nums) == 1:
                _num = float(_nums[1])

            # get the RSI value for current day
            rsi = self.__indicators_API.RSI(_num, current_day_index)

            # check that the value from {key: value} has a number in it
            # this is the trigger value
            _nums = re.findall(r'\d+', _value)
            if len(_nums) == 1:
                _trigger = float(_nums[1])
            else:
                print('Found invalid format RSI (invalid number found in trigger value)')
                # if no trigger value available, exit
                return None, True

            # trigger checks
            if '<=' in _value:
                if rsi <= _trigger:
                    _position = self.__create_position(df['Close'][current_day_index])
                    return _position, False
            elif '>=' in _value:
                if rsi >= _trigger:
                    _position = self.__create_position(df['Close'][current_day_index])
                    return _position, False
            elif '<' in _value:
                if rsi < _trigger:
                    _position = self.__create_position(df['Close'][current_day_index])
                    return _position, False
            elif '>' in _value:
                if rsi > _trigger:
                    _position = self.__create_position(df['Close'][current_day_index])
                    return _position, False
            elif '=' in _value:
                if rsi == _trigger:
                    _position = self.__create_position(df['Close'][current_day_index])
                    return _position, False

            # catch all case if nothing was hit (which is ok!)
            # No position and buying is still enabled
            return None, True

        def handle_SMA_buys() -> tuple:
            """Abstracted logic for SMA buy signals.

            return:
                tuple: The (Position, bool) tuple of the position created and the buying enabled signal

            Notes:
                This functions is internal (fxn inside fxn) which means everything in the outer
                function run() is global here
            """
            # get the unchecked trigger value from the strategy
            _value = self.__strategy['buy'][key]
            # find the SMA length, else exit
            _nums = re.findall(r'\d+', key)
            # since we have no default SMA, there must be a value provided, else exit
            if len(_nums) == 1:
                _num = int(_nums[1])

                # get the sma value for the current day
                sma = self.__indicators_API.SMA(_num, current_day_index)

                # check that the value from {key: value} has a number in it
                # this is the trigger value
                _nums = re.findall(r'\d+', _value)
                if len(_nums) == 1:
                    _trigger = float(_nums[1])
                else:
                    print('Found invalid format SMA (invalid number found in trigger value)')
                    # if no trigger value available, exit
                    return None, True

                # trigger checks
                if '<=' in _value:
                    if sma <= _trigger:
                        _position = self.__create_position(df['Close'][current_day_index])
                        return _position, False
                elif '>=' in _value:
                    if sma >= _trigger:
                        _position = self.__create_position(df['Close'][current_day_index])
                        return _position, False
                elif '<' in _value:
                    if sma < _trigger:
                        _position = self.__create_position(df['Close'][current_day_index])
                        return _position, False
                elif '>' in _value:
                    if sma > _trigger:
                        _position = self.__create_position(df['Close'][current_day_index])
                        return _position, False
                elif '=' in _value:
                    if sma == _trigger:
                        _position = self.__create_position(df['Close'][current_day_index])
                        return _position, False

                # catch all case if nothing was hit (which is ok!)
                return None, True

            print(f'Warning: {key} is in incorrect format and will be ignored')
            return None, True

        def handle_candle_stick_buys() -> tuple:
            """Abstracted logic for candle stick buy signals.

            return:
                tuple: The (Position, bool) tuple of the position created and the buying enabled signal.

            Notes:
                This functions is internal (fxn inside fxn) which means everything in the outer
                function run() is global here.
            """
            # find out how many keys there are
            num_keys = len(self.__strategy['buy'][key])

            # these will both need to be in ascending order [today, yesterday...]
            trigger_colors = list()
            actual_colors = list()

            # build the trigger list
            for _key in sorted(self.__strategy['buy'][key].keys()):
                trigger_colors.append(self.__strategy['buy'][key][_key])

            # build the actual list
            for i in range(num_keys):
                actual_colors.append(self.__indicators_API.candle_color(current_day_index - i))

            # check for trigger
            if actual_colors == trigger_colors:
                _position = self.__create_position(df['Close'][current_day_index])
                return _position, False

            # catch all case if nothing was hit (which is ok!)
            return None, True

        # ===================== Selling ===========================
        def handle_RSI_sells(_position) -> tuple:
            """Abstracted logic for RSI sell signals.

            return:
                tuple: The (Position, bool) tuple of the position created and the buying enabled signal

            Notes:
                This functions is internal (fxn inside fxn) which means everything in the outer
                function run() is global here

            """
            # get the unchecked trigger value from the strategy
            _value = self.__strategy['sell'][key]
            # find the value of the RSI else default
            _num = DEFAULT_RSI_LENGTH
            _nums = re.findall(r'\d+', key)
            if len(_nums) == 1:
                _num = float(_nums[1])

            # get the RSI value for current day
            rsi = self.__indicators_API.RSI(_num, current_day_index)

            # check that the value from {key: value} has a number in it
            # this is the trigger value
            _nums = re.findall(r'\d+', _value)
            if len(_nums) == 1:
                _trigger = float(_nums[1])
            else:
                print('Found invalid format RSI (invalid number found in trigger value)')
                # if no trigger value available, exit
                return _position, False

            # trigger checks
            if '<=' in _value:
                if rsi <= _trigger:
                    _position.close_position(df['Close'][current_day_index])
                    return None, True
            elif '>=' in _value:
                if rsi >= _trigger:
                    _position.close_position(df['Close'][current_day_index])
                    return None, True
            elif '<' in _value:
                if rsi < _trigger:
                    _position.close_position(df['Close'][current_day_index])
                    return None, True
            elif '>' in _value:
                if rsi > _trigger:
                    _position.close_position(df['Close'][current_day_index])
                    return None, True
            elif '=' in _value:
                if rsi == _trigger:
                    _position.close_position(df['Close'][current_day_index])
                    return None, True

            # catch all case if nothing was hit (which is ok!)
            # No position and buying is still enabled
            return _position, False

        def handle_SMA_sells(_position) -> tuple:
            """Abstracted logic for RSI sell signals.

            return:
                tuple: The (Position, bool) tuple of the position created and the buying enabled signal

            Notes:
                This functions is internal (fxn inside fxn) which means everything in the outer
                function run() is global here
            """
            # get the unchecked trigger value from the strategy
            _value = self.__strategy['sell'][key]
            # find the SMA length, else exit
            _nums = re.findall(r'\d+', key)
            # since we have no default SMA, there must be a value provided, else exit
            if len(_nums) == 1:
                _num = int(_nums[1])

                # get the sma value for the current day
                sma = self.__indicators_API.SMA(_num, current_day_index)

                # check that the value from {key: value} has a number in it
                # this is the trigger value
                _nums = re.findall(r'\d+', _value)
                if len(_nums) == 1:
                    _trigger = float(_nums[1])
                else:
                    print('Found invalid format SMA (invalid number found in trigger value)')
                    # if no trigger value available, exit
                    return _position, False

                # trigger checks
                if '<=' in _value:
                    if sma <= _trigger:
                        _position.close_position(df['Close'][current_day_index])
                        return None, True
                elif '>=' in _value:
                    if sma >= _trigger:
                        _position.close_position(df['Close'][current_day_index])
                        return None, True
                elif '<' in _value:
                    if sma < _trigger:
                        _position.close_position(df['Close'][current_day_index])
                        return None, True
                elif '>' in _value:
                    if sma > _trigger:
                        _position.close_position(df['Close'][current_day_index])
                        return None, True
                elif '=' in _value:
                    if sma == _trigger:
                        _position.close_position(df['Close'][current_day_index])
                        return None, True

                # catch all case if nothing was hit (which is ok!)
                return _position, False

            print(f'Warning: {key} is in incorrect format and will be ignored')
            return _position, False

        def handle_stop_profit_sells(_position) -> tuple:
            """Abstracted logic for stop profit sell signals.

            Args:
                _position (Position): The Position object to check.

            return:
                tuple: The (Position, bool) tuple of the Position (or None) and the buying enabled signal.

            Notes:
                This functions is internal (fxn inside fxn) which means everything in the outer
                function run() is global here.
            """
            # get the trigger from the strategy
            _trigger = float(self.__strategy['sell']['stop_profit'])

            # get the profit/loss from the strategy
            p_l = _position.profit_loss(df['Close'][current_day_index])

            # check for profit
            if p_l > 0:
                # check for trigger
                if p_l >= _trigger:
                    _position.close_position(df['Close'][current_day_index])
                    return None, True

            # catch all case if nothing was hit (which is ok!)
            return _position, False

        def handle_stop_loss_sells(_position) -> tuple:
            """Abstracted logic for stop loss sell signals.

            Args:
                _position (Position): The Position object to check.

            return:
                tuple: The (Position, bool) tuple of the Position (or None) and the buying enabled signal.

            Notes:
                This functions is internal (fxn inside fxn) which means everything in the outer
                function run() is global here.
            """
            # get the trigger from the strategy
            _trigger = float(self.__strategy['sell']['stop_loss'])

            # get the profit/loss from the position
            p_l = _position.profit_loss(df['Close'][current_day_index])

            # check for a loss
            if p_l < 0:
                # check trigger
                if abs(p_l) >= abs(_trigger):
                    _position.close_position(df['Close'][current_day_index])
                    return None, True

            # catch all case if nothing was hit (which is ok!)
            return _position, False

        def handle_candle_stick_sells(_position) -> tuple:
            """Abstracted logic for stop loss sell signals.

            Args:
                _position (Position): The Position object to check.

            return:
                tuple: The (Position, bool) tuple of the Position (or None) and the buying enabled signal.

            Notes:
                This functions is internal (fxn inside fxn) which means everything in the outer
                function run() is global here.
            """
            # find out how many keys there are
            num_keys = len(self.__strategy['sell'][key])

            # these will both need to be in ascending order [today, yesterday...]
            trigger_colors = list()
            actual_colors = list()

            # build the trigger list
            for _key in sorted(self.__strategy['sell'][key].keys()):
                trigger_colors.append(self.__strategy['sell'][key][_key])

            # build the actual list
            for i in range(num_keys):
                actual_colors.append(self.__indicators_API.candle_color(current_day_index - i))

            # check for trigger
            if actual_colors == trigger_colors:
                _position.close_position(df['Close'][current_day_index])
                return None, True

            # catch all case if nothing was hit (which is ok!)
            return _position, False

        # set the objects symbol to the passed value, so we can use it everywhere
        self.__symbol = symbol.upper()

        # check the strategy for errors
        self.__error_check_strategy()

        # parse the strategy so we know what the user wants
        self.__parse_strategy()

        # get the data from the servers
        df = self.__broker_API.get_daily_data(self.__symbol, self.__augmented_start_date_unix, self.__end_date_unix)
        # FIXME: This should fetch use the correct amount of data
        #   now we can start working on the looping logic

        # FIXME: Before we can start looping, we need to figure out how many days we need to loop across

        # initialize the indicators API with the data
        self.__indicators_API = Indicators(df)

        # len(df['close']) does the same thing as the below line
        total_days = int((self.__end_date_unix - self.__augmented_start_date_unix) / SECONDS_PER_DAY)
        days_in_focus = int((self.__end_date_unix - self.__start_date_unix) / SECONDS_PER_DAY)

        focus_start_day = total_days - days_in_focus

        buy_mode = True
        position = None

        # REMINDER: we want to give the user control of the start and end day
        # DUE TO WEEKENDS AND HOLIDAYS, the window size will most likely not be the expected amount of days
        # BUT WE ENSURE SUFFICIENT DATA in the parse_strategy() function
        for current_day_index in range(focus_start_day, len(df['Close'])):
            # we loop from the focus start day (200)
            # to the total amount of days in the set (400)
            # the day_index represents the index of the current day in the
            # data set, so if we need something like SMA200 we just get all
            # the days from now to now-200
            # we can have an indicator package like viper that takes a df
            # a start and an end day and calculate the SMA X

            # --- debug ----
            os.system('cls')
            print(f'Current Day index: {current_day_index}')
            # print(f'Starting day: {focus_start_day}')
            # print(f'Total window size: {len(df["Close"])}')
            # --- debug ----

            # --- testing ---
            # --- testing ---

            if buy_mode:
                buy_keys = self.__strategy['buy'].keys()
                for key in buy_keys:
                    if 'RSI' in key:
                        position, buy_mode = handle_RSI_buys()
                        if not buy_mode:
                            break
                    if 'SMA' in key:
                        position, buy_mode = handle_SMA_buys()
                        if not buy_mode:
                            break
                    if key == 'color':
                        position, buy_mode = handle_candle_stick_buys()
                        if not buy_mode:
                            break
            else:
                # sell mode
                sell_keys = self.__strategy['sell'].keys()
                for key in sell_keys:
                    if 'RSI' in key:
                        position, buy_mode = handle_RSI_sells(position)
                        if buy_mode:
                            break
                    if 'SMA' in key:
                        position, buy_mode = handle_SMA_sells(position)
                        if buy_mode:
                            break
                    if key == 'stop_loss':
                        position, buy_mode = handle_stop_loss_sells(position)
                        if buy_mode:
                            break
                    if key == 'stop_profit':
                        position, buy_mode = handle_stop_profit_sells(position)
                        if buy_mode:
                            break
                    if key == 'color':
                        position, buy_mode = handle_candle_stick_sells(position)

        # FIXME: We need to put x more days in the query
        #   - Then we have data to work with on day 1 of the user requesting it
        #   - RSI is 14, but what about something wild like SMA 200?
        #   - A workaround for something like that is working out what indicators
        #   - the user wants before requesting the data.

        # FIXME:
        #   - Step 1: User enters a strategy
        #   - Step 2: We need to parse that strategy for errors and modded dates
        #   -   Set them to self.augmented_start_unix

        # start 5 days in so we have some data
        for index in range(5, len(df['Close'])):
            pass

        """
        for bar in data['bars'][self.__symbol]:
            if buy_mode:
                pass
            else:
                # sell mode
                if self.__stop_profit:
                    # sell position
                    pass
                if self.__stop_loss:
                    # sell position
                    pass
        """

# convert the keys to plaintext and make them env vars so we can put this on github
