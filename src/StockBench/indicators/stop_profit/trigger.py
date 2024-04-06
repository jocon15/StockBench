import logging
from StockBench.indicator.trigger import Trigger

log = logging.getLogger()


class StopProfitTrigger(Trigger):
    def __init__(self, strategy_symbol):
        super().__init__(strategy_symbol, side=Trigger.SELL)

    def additional_days(self, key, value) -> int:
        """Calculate the additional days required.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from the strategy.
        """
        # note stop profit does not require additional days
        return 0

    def add_to_data(self, key, value, side, data_manager):
        """Add data to the dataframe.

        Args:
            key (any): The key value from the strategy.
            value (any): The value from thr strategy.
            side (str): The side (buy/sell).
            data_manager (any): The data object.
        """
        # note stop profit trigger is not an additional indicator and does not
        # require any additional data to be added to the data
        return

    def check_trigger(self, key, value, data_manager, position_obj, current_day_index) -> bool:
        """Trigger logic for stop profit.

        Args:
            key (str): The key value of the trigger.
            value (str): The value of the trigger.
            data_manager (any): The data API object.
            position_obj (any): The position object.
            current_day_index (int): The index of the current day.

        return:
            bool: True if the trigger was hit.
        """
        log.debug('Checking stop profit trigger...')

        # get the current price
        current_price = data_manager.get_data_point(data_manager.CLOSE, current_day_index)
        open_price = data_manager.get_data_point(data_manager.OPEN, current_day_index)

        # get the profit/loss values from the position
        intraday_pl = position_obj.intraday_profit_loss(open_price, current_price)
        lifetime_pl = position_obj.profit_loss(current_price)

        # get the profit/loss percents from the position
        intraday_plpc = position_obj.intraday_profit_loss_percent(open_price, current_price)
        lifetime_plpc = position_obj.profit_loss_percent(current_price)

        if 'intraday' in key:
            # use intraday stats
            if intraday_pl > 0:
                # the position is at a profit (plpc will be a loss if pl is a profit)
                if '%' in value:
                    # use value percent stats
                    nums = self.find_all_nums_in_str(value)
                    trigger_value = float(nums[0])
                    # check trigger
                    if intraday_plpc >= trigger_value:
                        log.info('Stop profit trigger hit!')
                        return True
                else:
                    # use value stats
                    trigger_value = float(value)
                    # check trigger
                    if intraday_pl >= trigger_value:
                        log.info('Stop profit trigger hit!')
                        return True
        else:
            if lifetime_pl > 0:
                # the position is at a profit (plpc will be a loss if pl is a profit)
                # use lifetime stats
                if '%' in value:
                    # use value percent stats
                    nums = self.find_all_nums_in_str(value)
                    trigger_value = float(nums[0])
                    # check trigger
                    if lifetime_plpc >= trigger_value:
                        log.info('Stop profit trigger hit!')
                        return True
                else:
                    # use value stats
                    trigger_value = float(value)
                    # check trigger
                    if lifetime_pl >= trigger_value:
                        log.info('Stop profit trigger hit!')
                        return True

        log.debug('Stop profit trigger checked')

        # trigger was not hit
        return False
