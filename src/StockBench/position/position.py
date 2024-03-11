class Position:
    """This class defines a position object.

    A position is one or more shares purchased at the same price for a particular asset. The position objects is
    needed because we need to keep tract of the purchase price of those shares. In the context of a simulation,
    the position is going to be opened on one day, likely held for some time, then liquidated. At the liquidation
    point, we want to have all the details regarding that position in one place for analytical purposes."""
    def __init__(self, buy_price: float, share_count: float, current_day_index: int):
        self.buy_day_index = int(current_day_index)
        self.sell_day_index = None

        self.__buy_price = float(buy_price)
        self.__sell_price = None
        self.__share_count = float(share_count)

    def close_position(self, sell_price: float, current_day_index: int):
        """ Close the position.

        Args:
            sell_price (float): The sell price of the position.
            current_day_index (int): The index of the day that the position was closed on.
        """
        self.__sell_price = float(sell_price)
        self.sell_day_index = int(current_day_index)

    def profit_loss(self, current_price: float) -> float:
        """Calculate the profit/loss for the position for a current price

        Args:
            current_price (float): The current price of the asset.

        return:
            float: The current profit/loss value of the position.
        """
        initial_value = self.__share_count * self.__buy_price
        current_value = self.__share_count * float(current_price)
        return current_value - initial_value

    def intraday_profit_loss(self, open_price: float, current_price: float):
        """Calculate the intraday profit/loss for a position.

        Args:
            open_price (float): Today's opening price for the symbol.
            current_price (float): Today's current price for the symbol.

        return:
            float: The intraday profit/loss value of the position.
        """
        open_value = self.__share_count * float(open_price)
        current_value = self.__share_count * float(current_price)
        return current_value - open_value

    def lifetime_profit_loss(self) -> float:
        """Calculate the profit/loss for a closed position.

        return:
            float: The profit/loss value of the position.
        """
        if not self.__sell_price:
            raise Exception('You need to close the position first')
        initial_value = self.__share_count * self.__buy_price
        current_value = self.__share_count * self.__sell_price
        return current_value - initial_value

    def profit_loss_percent(self, current_price: float):
        """Calculate the profit/loss percent for the position for a current price

        Args:
            current_price (float): The current price of the asset.

        return:
            float: The current profit/loss percent value of the position.
        """
        return round(((float(current_price) - self.__buy_price) / self.__buy_price) * 100.0, 2)

    @staticmethod
    def intraday_profit_loss_percent(open_price: float, current_price: float) -> float:
        """Calculate the intraday profit/loss percent for a position.

        Args:
            open_price (float): Today's opening price for the symbol.
            current_price (float): Today's current price for the symbol.

        return:
            float: The intraday profit/loss percent value of the position.
        """
        return round(((float(current_price) - float(open_price)) / float(open_price)) * 100.0, 2)

    def lifetime_profit_loss_percent(self) -> float:
        """Calculate the profit/loss percent for a closed position.

        return:
            float: The profit/loss percent value of the position.
        """
        if not self.__sell_price:
            raise Exception('You need to close the position first')
        return round(((self.__sell_price - self.__buy_price) / self.__buy_price) * 100.0, 2)

    def get_buy_price(self):
        """Accessor for the purchase price of the position.

        return:
            float: The purchase price.
        """
        return self.__buy_price

    def get_share_count(self):
        """Accessor for the share count of the position.

        return:
            float: The share count.
        """
        return self.__share_count

    def get_sell_price(self):
        """Accessor for the liquidation price of the position.

        return:
            float: The liquidation price.
        """
        return self.__sell_price
