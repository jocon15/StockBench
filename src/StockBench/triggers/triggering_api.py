class TriggerAPI:
    """"""
    # FIXME: no buying happens in this class - remove it (position creation)
    # FIXME: ^ remove all insert buy/insert sell stuff

    def __init__(self, strategy):
        # strategy does not get cleared
        self.__strategy = strategy
        # All below attributes get cleared after trigger call
        self.__data_object = None
        self.__position_object = None
        self.__current_day_index = None

    def check_buy_triggers(self, data_obj, current_day_index) -> bool:
        self.__data_object = data_obj
        self.__current_day_index = current_day_index

        was_triggered = False
        # old logic
        buy_keys = self.__strategy['buy'].keys()
        for key in buy_keys:
            if 'and' in key:
                # handle and triggers
                was_triggered = self.__handle_and_buy_triggers()
                if was_triggered:
                    break
            else:
                # handle or triggers
                was_triggered = self.__handle_or_buy_triggers()
                if not was_triggered:
                    break

        self.__clear_attributes()
        return was_triggered

    def check_sell_triggers(self, data_obj, position_obj, current_day_index) -> bool:
        self.__data_object = data_obj
        self.__position_object = position_obj
        self.__current_day_index = current_day_index

        was_triggered = False
        # old logic
        # sell mode
        sell_keys = self.__strategy['sell'].keys()
        for key in sell_keys:
            if 'and' in key:
                # handle and triggers
                was_triggered = self.__handle_and_sell_triggers()
                if was_triggered:
                    break
            else:
                # handle or triggers
                was_triggered = self.__handle_or_sell_triggers()
                if was_triggered:
                    break

        self.__clear_attributes()
        return was_triggered

    def __clear_attributes(self):
        self.__data_object = None
        self.__position_object = None
        self.__current_day_index = None

    # ===================== Buying ==========================
    def __handle_or_buy_triggers(self) -> bool:
        """Abstraction for sorting the buy triggers with OR logic."""
        _position = None
        trigger_hit = False

        # check for all types of triggers
        if 'RSI' in key:
            trigger_hit = check_rsi_trigger(key, self.__strategy['buy'][key])
        elif 'SMA' in key:
            trigger_hit = check_sma_trigger(key, self.__strategy['buy'][key])
        elif 'volume' in key:
            trigger_hit = check_volume_trigger(self.__strategy['buy'][key])
        elif key == 'color':
            trigger_hit = check_candle_colors_trigger(self.__strategy['buy'][key])
        elif key == 'price':
            trigger_hit = check_price_trigger(self.__strategy['buy'][key])

        if trigger_hit:
            # create the position
            _position = self.__create_position(current_day_index)
            insert_buy()
            return _position, False

        # trigger was not hit
        return _position, True

    def __handle_and_buy_triggers(self) -> bool:
        """ Abstraction for sorting the buy triggers with AND logic

        Notes:
             This is an AND comparison so all operands need to evaluate to true
        """
        _position = None
        for inner_key in self.__strategy['buy'][key].keys():
            # reset trigger indicator
            trigger_hit = False
            # check for all types of triggers
            if 'RSI' in inner_key:
                trigger_hit = check_rsi_trigger(inner_key, self.__strategy['buy'][key][inner_key])
            elif 'SMA' in inner_key:
                trigger_hit = check_sma_trigger(inner_key, self.__strategy['buy'][key][inner_key])
            elif 'volume' in key:
                trigger_hit = check_volume_trigger(self.__strategy['buy'][key])
            elif inner_key == 'color':
                trigger_hit = check_candle_colors_trigger(self.__strategy['buy'][key][inner_key])
            elif key == 'price':
                trigger_hit = check_price_trigger(self.__strategy['buy'][key][inner_key])

            if not trigger_hit:
                # not all triggers were hit
                return _position, True
        # all triggers were hit

        # create the position
        _position = self.__create_position(current_day_index)
        insert_buy()
        return _position, False

    # ===================== Selling ===========================

    def __handle_or_sell_triggers(self) -> bool:
        """Abstraction for sorting the buy triggers with OR logic."""
        trigger_hit = False

        # check for all types of triggers
        if 'RSI' in key:
            trigger_hit = check_rsi_trigger(key, self.__strategy['sell'][key])
        elif 'SMA' in key:
            trigger_hit = check_sma_trigger(key, self.__strategy['sell'][key])
        elif 'volume' in key:
            trigger_hit = check_volume_trigger(self.__strategy['buy'][key])
        elif key == 'stop_loss':
            trigger_hit = check_stop_loss_trigger(self.__strategy['sell'][key])
        elif key == 'stop_profit':
            trigger_hit = check_stop_profit_trigger(self.__strategy['sell'][key])
        elif key == 'color':
            trigger_hit = check_candle_colors_trigger(self.__strategy['sell'][key])
        elif key == 'price':
            trigger_hit = check_price_trigger(self.__strategy['sell'][key])

        if trigger_hit:
            # create the position
            self.__liquidate_position(position, current_day_index)
            insert_sell()
            return None, True

        # trigger was not hit
        return position, False

    def __handle_and_sell_triggers(self) -> bool:
        """ Abstraction for sorting the sell triggers with AND logic

        Notes:
             This is an AND comparison so all operands need to evaluate to true
        """
        for inner_key in self.__strategy['sell'][key].keys():
            # reset trigger indicator
            trigger_hit = False
            # check for all types of triggers
            if 'RSI' in inner_key:
                trigger_hit = check_rsi_trigger(inner_key, self.__strategy['sell'][key][inner_key])
            elif 'SMA' in inner_key:
                trigger_hit = check_sma_trigger(inner_key, self.__strategy['sell'][key][inner_key])
            elif 'volume' in key:
                trigger_hit = check_volume_trigger(self.__strategy['buy'][key])
            elif inner_key == 'stop_loss':
                trigger_hit = check_stop_loss_trigger(self.__strategy['sell'][key][inner_key])
            elif inner_key == 'stop_profit':
                trigger_hit = check_stop_profit_trigger(self.__strategy['sell'][key][inner_key])
            elif inner_key == 'color':
                trigger_hit = check_candle_colors_trigger(self.__strategy['sell'][key][inner_key])
            elif key == 'price':
                trigger_hit = check_price_trigger(self.__strategy['sell'][key])

            if not trigger_hit:
                # not all triggers were hit
                return position, False
        # all triggers were hit

        # liquidate the position
        self.__liquidate_position(position, current_day_index)
        insert_sell()
        return None, True

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
            # FIXME: need to be able to use the constants file
            #   (https://www.geeksforgeeks.org/python-import-module-from-different-directory/)
            if (indicator_value - trigger_value) <= 0.001:  # DOUBLE_COMPARISON_EPSILON:
                return True
        return False

    def __check_rsi_trigger(_key, _value) -> bool:
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
        rsi = self.__df['RSI'][current_day_index]

        if CURRENT_PRICE_SYMBOL in _value:
            trigger = self.__df['Close'][current_day_index]
            operator = _value.replace('$price', '')
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
        result = basic_triggers_check(rsi, operator, trigger)

        log.debug('All RSI triggers checked')

        return result

    def __check_sma_trigger(_key, _value) -> bool:
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
            sma = self.__df[title][current_day_index]

            if CURRENT_PRICE_SYMBOL in _value:
                trigger = self.__df['Close'][current_day_index]
                operator = _value.replace('$price', '')
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
            result = basic_triggers_check(sma, operator, trigger)

            log.debug('All SMA triggers checked')

            return result

        log.warning(f'Warning: {key} is in incorrect format and will be ignored')
        print(f'Warning: {key} is in incorrect format and will be ignored')
        return False

    def __check_volume_trigger(_value) -> bool:
        """"""
        volume = self.__df['volume'][current_day_index]

        if CURRENT_PRICE_SYMBOL in _value:
            trigger = self.__df['Close'][current_day_index]
            operator = _value.replace('$price', '')
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
        result = basic_triggers_check(volume, operator, trigger)

        log.debug('All volume triggers checked')

        return result

    def __check_candle_colors_trigger(_value) -> bool:
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
            actual_colors.append(self.__indicators_API.candle_color(current_day_index - i))

        # check for trigger
        if actual_colors == trigger_colors:
            log.info('Candle stick trigger hit!')
            return True

        log.debug('All candle stick triggers checked')

        # catch all case if nothing was hit (which is ok!)
        return False

    def __check_price_trigger(_value):
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

        price = self.__df['Close'][current_day_index]

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
        result = basic_triggers_check(price, operator, trigger)

        log.debug('All Price triggers checked')

        # catch all case if nothing was hit (which is ok!)
        return result

    def __check_stop_profit_trigger(_value) -> bool:
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

    def __check_stop_loss_trigger(_value) -> bool:
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