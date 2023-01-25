import re
import logging
from StockBench.constants import *

log = logging.getLogger()


class TriggerAPI:
    """This class defines a TriggerAPI object.

    The TriggerAPI object is designed to be used as an API for the simulator to abstract the triggering methods for
    each rule. To keep it simple for the simulator, there are 2 defined entry points, check buy and check sell
    triggers. The rest of the complex triggering logic gets implemented here.

    The goal of the 2 API functions is to return a boolean. True = trigger hit. False = trigger not hit. Both of these
    return values hold for buy or sell.
    """
    def __init__(self, strategy):
        # strategy does not get cleared
        self.__strategy = strategy
        # All below attributes get cleared after trigger call
        self.__data_object = None
        self.__position_object = None
        self.__current_day_index = None

    def check_buy_triggers(self, data_obj, current_day_index) -> bool:
        """Check all buy triggers.

        Args:
            data_obj (object): The data object.
            current_day_index (int): The index of the current day.

        returns:
            bool: True if triggered, False otherwise.
        """
        self.__data_object = data_obj
        self.__current_day_index = current_day_index

        was_triggered = False
        buy_keys = self.__strategy['buy'].keys()
        for key in buy_keys:
            if 'and' in key:
                # handle and triggers
                was_triggered = self.__handle_and_buy_triggers(key)
                if was_triggered:
                    break
            else:
                # handle or triggers
                was_triggered = self.__handle_or_buy_triggers(key)
                if was_triggered:
                    break

        self.__clear_attributes()
        return was_triggered

    def check_sell_triggers(self, data_obj, position_obj, current_day_index) -> bool:
        """Check all buy triggers.

        Args:
            data_obj (object): The data object.
            position_obj (object): The position object.
            current_day_index (int): The index of the current day.

        returns:
            bool: True if triggered, False otherwise.
        """
        self.__data_object = data_obj
        self.__position_object = position_obj
        self.__current_day_index = current_day_index

        was_triggered = False
        sell_keys = self.__strategy['sell'].keys()
        for key in sell_keys:
            if 'and' in key:
                # handle and triggers
                was_triggered = self.__handle_and_sell_triggers(key)
                if was_triggered:
                    break
            else:
                # handle or triggers
                was_triggered = self.__handle_or_sell_triggers(key)
                if was_triggered:
                    break

        self.__clear_attributes()
        return was_triggered

    def __clear_attributes(self):
        self.__data_object = None
        self.__position_object = None
        self.__current_day_index = None

    # ===================== Buying ==========================
    def __handle_or_buy_triggers(self, _key) -> bool:
        """Abstraction for sorting the buy triggers with OR logic."""
        _position = None
        trigger_hit = False

        # check for all types of triggers
        if 'RSI' in _key:
            trigger_hit = self.__check_rsi_trigger(_key, self.__strategy['buy'][_key])
        elif 'SMA' in _key:
            trigger_hit = self.__check_sma_trigger(_key, self.__strategy['buy'][_key])
        elif 'volume' in _key:
            trigger_hit = self.__check_volume_trigger(self.__strategy['buy'][_key])
        elif _key == 'color':
            trigger_hit = self.__check_candle_colors_trigger(self.__strategy['buy'][_key])
        elif _key == 'price':
            trigger_hit = self.__check_price_trigger(self.__strategy['buy'][_key])

        if trigger_hit:
            # create the position
            return True

        # trigger was not hit
        return False

    def __handle_and_buy_triggers(self, _key) -> bool:
        """ Abstraction for sorting the buy triggers with AND logic

        Notes:
             This is an AND comparison so all operands need to evaluate to true
        """
        _position = None
        for inner_key in self.__strategy['buy'][_key].keys():
            # reset trigger indicator
            trigger_hit = False
            # check for all types of triggers
            if 'RSI' in inner_key:
                trigger_hit = self.__check_rsi_trigger(inner_key, self.__strategy['buy'][_key][inner_key])
            elif 'SMA' in inner_key:
                trigger_hit = self.__check_sma_trigger(inner_key, self.__strategy['buy'][_key][inner_key])
            elif 'volume' in _key:
                trigger_hit = self.__check_volume_trigger(self.__strategy['buy'][_key])
            elif inner_key == 'color':
                trigger_hit = self.__check_candle_colors_trigger(self.__strategy['buy'][_key][inner_key])
            elif _key == 'price':
                trigger_hit = self.__check_price_trigger(self.__strategy['buy'][_key][inner_key])

            if not trigger_hit:
                # not all triggers were hit
                return False

        # all triggers were hit
        return True

    # ===================== Selling ===========================

    def __handle_or_sell_triggers(self, _key) -> bool:
        """Abstraction for sorting the buy triggers with OR logic."""
        trigger_hit = False

        # check for all types of triggers
        if 'RSI' in _key:
            trigger_hit = self.__check_rsi_trigger(_key, self.__strategy['sell'][_key])
        elif 'SMA' in _key:
            trigger_hit = self.__check_sma_trigger(_key, self.__strategy['sell'][_key])
        elif 'volume' in _key:
            trigger_hit = self.__check_volume_trigger(self.__strategy['buy'][_key])
        elif _key == 'stop_loss':
            trigger_hit = self.__check_stop_loss_trigger(self.__strategy['sell'][_key])
        elif _key == 'stop_profit':
            trigger_hit = self.__check_stop_profit_trigger(self.__strategy['sell'][_key])
        elif _key == 'color':
            trigger_hit = self.__check_candle_colors_trigger(self.__strategy['sell'][_key])
        elif _key == 'price':
            trigger_hit = self.__check_price_trigger(self.__strategy['sell'][_key])

        if trigger_hit:
            return True

        # trigger was not hit
        return False

    def __handle_and_sell_triggers(self, _key) -> bool:
        """ Abstraction for sorting the sell triggers with AND logic

        Notes:
             This is an AND comparison so all operands need to evaluate to true
        """
        for inner_key in self.__strategy['sell'][_key].keys():
            # reset trigger indicator
            trigger_hit = False
            # check for all types of triggers
            if 'RSI' in inner_key:
                trigger_hit = self.__check_rsi_trigger(inner_key, self.__strategy['sell'][_key][inner_key])
            elif 'SMA' in inner_key:
                trigger_hit = self.__check_sma_trigger(inner_key, self.__strategy['sell'][_key][inner_key])
            elif 'volume' in _key:
                trigger_hit = self.__check_volume_trigger(self.__strategy['buy'][_key])
            elif inner_key == 'stop_loss':
                trigger_hit = self.__check_stop_loss_trigger(self.__strategy['sell'][_key][inner_key])
            elif inner_key == 'stop_profit':
                trigger_hit = self.__check_stop_profit_trigger(self.__strategy['sell'][_key][inner_key])
            elif inner_key == 'color':
                trigger_hit = self.__check_candle_colors_trigger(self.__strategy['sell'][_key][inner_key])
            elif _key == 'price':
                trigger_hit = self.__check_price_trigger(self.__strategy['sell'][_key])

            if not trigger_hit:
                # not all triggers were hit
                return False

        # all triggers were hit
        return True

    # ===================== Triggers ===========================

    @staticmethod
    def __basic_triggers_check(indicator_value, operator_value, trigger_value) -> bool:
        """Abstraction for basic trigger comparison operators.

        Args:
            indicator_value (float): The value of the indicator.
            operator_value (str): The operator defined in the strategy
            trigger_value (float): The value of the trigger.

        returns:
            bool: True if the trigger was hit.
        """
        if operator_value == '<=':
            if indicator_value <= trigger_value:
                return True
        elif operator_value == '>=':
            if indicator_value >= trigger_value:
                return True
        elif operator_value == '<':
            if indicator_value < trigger_value:
                return True
        elif operator_value == '>':
            if indicator_value > trigger_value:
                return True
        elif operator_value == '=':
            if (indicator_value - trigger_value) <= 0.001:  # DOUBLE_COMPARISON_EPSILON:
                return True
        return False

    def __check_rsi_trigger(self, _key, _value) -> bool:
        """Abstracted logic for RSI triggers.

        Args:
            _key (str): The key value of the trigger.
            _value (str): The value of the trigger.

        return:
            bool: True if the trigger was hit.

        Notes:
            This functions is internal (fxn inside fxn) which means everything in the outer
            function run() is global here
        """
        log.debug('Checking RSI triggers...')

        # find the value of the RSI else default
        _num = DEFAULT_RSI_LENGTH
        _nums = re.findall(r'\d+', _key)
        if len(_nums) == 1:
            _num = float(_nums[0])

        # get the RSI value for current day
        # old way where we calculate it on the spot (deprecated)
        # rsi = self.__indicators_API.RSI(_num, current_day_index)
        # new way where we just pull the pre-calculated value from the col in the df
        rsi = self.__data_object.get_data_point('RSI', self.__current_day_index)

        if CURRENT_PRICE_SYMBOL in _value:
            trigger = float(self.__data_object.get_data_point(self.__data_object.CLOSE, self.__current_day_index))
            operator = _value.replace(CURRENT_PRICE_SYMBOL, '')
        else:
            # check that the value from {key: value} has a number in it
            # this is the trigger value
            _nums = re.findall(r'\d+', _value)
            if len(_nums) == 1:
                trigger = float(_nums[0])
                operator = _value.replace(str(_nums[0]), '')
            else:
                log.warning('Found invalid format RSI (invalid number found in trigger value)')
                print('Found invalid format RSI (invalid number found in trigger value)')
                # if no trigger value available, exit
                return False

        # trigger checks
        result = self.__basic_triggers_check(rsi, operator, trigger)

        log.debug('All RSI triggers checked')

        return result

    def __check_sma_trigger(self, _key, _value) -> bool:
        """Abstracted logic for SMA triggers.

        Args:
            _key (str): The key value of the trigger.
            _value (str): The value of the trigger.

        return:
            bool: True if the trigger was hit.

        Notes:
            This functions is internal (fxn inside fxn) which means everything in the outer
            function run() is global here
        """
        log.debug('Checking SMA triggers...')

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
            sma = self.__data_object.get_data_point(title, self.__current_day_index)

            if CURRENT_PRICE_SYMBOL in _value:
                trigger = float(self.__data_object.get_data_point(self.__data_object.CLOSE, self.__current_day_index))
                operator = _value.replace(CURRENT_PRICE_SYMBOL, '')
            else:
                # check that the value from {key: value} has a number in it
                # this is the trigger value
                _nums = re.findall(r'\d+', _value)
                if len(_nums) == 1:
                    trigger = float(_nums[0])
                    operator = _value.replace(str(_nums[0]), '')
                else:
                    print('Found invalid format SMA (invalid number found in trigger value)')
                    # if no trigger value available, exit
                    return False

            # trigger checks
            result = self.__basic_triggers_check(sma, operator, trigger)

            log.debug('All SMA triggers checked')

            return result

        log.warning(f'Warning: {_key} is in incorrect format and will be ignored')
        print(f'Warning: {_key} is in incorrect format and will be ignored')
        return False

    def __check_volume_trigger(self, _value) -> bool:
        """"""
        volume = self.__data_object.get_data_point(self.__data_object.VOLUME, self.__current_day_index)

        if CURRENT_PRICE_SYMBOL in _value:
            trigger = float(self.__data_object.get_data_point(self.__data_object.CLOSE, self.__current_day_index))
            operator = _value.replace(CURRENT_PRICE_SYMBOL, '')
        else:
            # check that the value from {key: value} has a number in it
            # this is the trigger value
            _nums = re.findall(r'\d+', _value)
            if len(_nums) == 1:
                trigger = float(_nums[0])
                operator = _value.replace(str(_nums[0]), '')
            else:
                print('Found invalid format SMA (invalid number found in trigger value)')
                # if no trigger value available, exit
                return False

        # trigger checks
        result = self.__basic_triggers_check(volume, operator, trigger)

        log.debug('All volume triggers checked')

        return result

    def __check_candle_colors_trigger(self, _value) -> bool:
        """Abstracted logic for candle stick triggers.

        Args:
            _value (dict): The value of the trigger.

        return:
            bool: True if the trigger was hit.

        Notes:
            This functions is internal (fxn inside fxn) which means everything in the outer
            function run() is global here.
        """
        log.debug('Checking candle stick triggers...')

        # find out how many keys there are (_value is a dict)
        num_keys = len(_value)

        # these will both need to be in ascending order [today, yesterday...]
        trigger_colors = list()
        actual_colors = list()

        # build the trigger list
        for _key in sorted(_value.keys()):
            candle_color = _value[_key]
            if candle_color == 'green':
                trigger_colors.append(1)
            else:
                trigger_colors.append(0)

        # build the actual list
        for i in range(num_keys):
            actual_colors.append(self.__data_object.get_data_point(self.__data_object.COLOR, self.__current_day_index))

        # check for trigger
        if actual_colors == trigger_colors:
            log.info('Candle stick trigger hit!')
            return True

        log.debug('All candle stick triggers checked')

        # catch all case if nothing was hit (which is ok!)
        return False

    def __check_price_trigger(self, _value):
        """Abstracted logic for price triggers.

        Args:
            _value (str): The value of the trigger.

        return:
            bool: True if the trigger was hit.

        Notes:
            This functions is internal (fxn inside fxn) which means everything in the outer
            function run() is global here.
        """
        log.debug('Checking price triggers...')

        price = self.__data_object.get_data_point(self.__data_object.CLOSE, self.__current_day_index)

        # check that the value from {key: value} has a number in it
        # this is the trigger value
        _nums = re.findall(r'\d+', _value)
        if len(_nums) == 1:
            trigger = float(_nums[0])
            operator = _value.replace(str(_nums[0]), '')
        else:
            print('Found invalid format price (invalid number found in trigger value)')
            # if no trigger value available, exit
            return False

        # trigger checks
        result = self.__basic_triggers_check(price, operator, trigger)

        log.debug('All Price triggers checked')

        # catch all case if nothing was hit (which is ok!)
        return result

    def __check_stop_profit_trigger(self, _value) -> bool:
        """Abstracted logic for stop profit triggers.

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

        # get the current price
        price = self.__data_object.get_data_point(self.__data_object.CLOSE, self.__current_day_index)

        # get the profit/loss from the strategy
        p_l = self.__position_object.profit_loss(price)

        # check for profit
        if p_l > 0:
            # check for trigger
            if p_l >= _trigger:
                log.info('Stop profit trigger hit!')
                return True

        log.debug('Stop profit triggers checked')

        # catch all case if nothing was hit (which is ok!)
        return False

    def __check_stop_loss_trigger(self, _value) -> bool:
        """Abstracted logic for stop loss triggers.

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

        # get the current price
        price = self.__data_object.get_data_point(self.__data_object.CLOSE, self.__current_day_index)

        # get the profit/loss from the strategy
        p_l = self.__position_object.profit_loss(price)

        # check for a loss
        if p_l < 0:
            # check trigger
            if abs(p_l) >= abs(_trigger):
                log.info('Stop loss trigger hit!')
                return True

        log.debug('Stop loss triggers checked')

        # catch all case if nothing was hit (which is ok!)
        return False
