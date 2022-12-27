# FIXME:
#   - This class represents a position object. A position is where we purchase an asset.
#   - When we purchase an asset, we have a share count and a share price.
#   - While the position is alive, there is no sell_price, yet.
#   - But we can calculate the profit/loss of the live position at any time given the
#   - current price of the asset.

class Position:
    def __init__(self, _buy_price: float, _share_count: float):
        self.__buy_price = _buy_price
        self.__sell_price = None
        self.__share_count = _share_count

    def close_position(self, _sell_price: float):
        """ Close the position.

        Args:
            _sell_price (float): The sell price of the position.
        """
        self.__sell_price = _sell_price

    def profit_loss(self, _current_price: float) -> float:
        """Calculate the profit/loss for the position for a current price

        Args:
            _current_price (float): The current price of the asset.

        return:
            float: The current profit/loss value of the position.
        """
        initial_value = self.__share_count * self.__buy_price
        current_value = self.__share_count * _current_price
        return current_value - initial_value

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

    def get_buy_price(self):
        return self.__buy_price

    def get_share_count(self):
        return self.__share_count

    def get_sell_price(self):
        return self.__sell_price
