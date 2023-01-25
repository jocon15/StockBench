class UserAccount:
    """This class defines a user account object.

    This class is intended to be used as a singleton. The account object keeps track of the users account for
    analytical purposes.
    """
    def __init__(self, balance: float):
        # don't check for negative yet in case we implement leverage trading
        self.__balance = float(balance)
        self.__initial_balance = float(balance)

    def get_balance(self):
        return round(self.__balance, 2)

    def deposit(self, value: float):
        self.__balance += float(value)

    def withdraw(self, value: float):
        self.__balance -= float(value)

    def get_profit_loss(self):
        return round(self.__balance - self.__initial_balance, 2)
