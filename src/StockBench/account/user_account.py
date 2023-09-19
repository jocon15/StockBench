class UserAccount:
    """This class defines a user account object.

    This class is intended to be used as a singleton. The account object keeps track of the users account for
    analytical purposes.
    """
    def __init__(self, balance: float):
        """Constructor

        Args:
            balance (float): The starting balance of the account
        """
        # don't check for negative yet in case we implement leverage trading
        self.__balance = float(balance)
        self.__initial_balance = float(balance)

    def deposit(self, value: float):
        """Deposit money into the account.

        Args:
            value (float): The value to add to the account.
        """
        self.__balance += float(value)

    def withdraw(self, value: float):
        """Withdraw money from the account.

        Args:
            value (float): The value to remove from the account.
        """
        self.__balance -= float(value)

    def reset(self):
        """Reset the account balance to the initial amount."""
        self.__balance = self.__initial_balance

    def get_balance(self) -> float:
        """Get the current balance of the account.

        returns:
            float: The balance of the account.
        """
        return round(self.__balance, 2)

    def get_profit_loss(self) -> float:
        """Get the current profit/loss of the account.

        returns:
            float: The profit/loss amount.
        """
        return round(self.__balance - self.__initial_balance, 2)
