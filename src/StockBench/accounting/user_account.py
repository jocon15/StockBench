

class UserAccount:

    def __init__(self, balance: float):
        self.__balance = balance
        self.__initial_balance = balance

    def get_balance(self):
        return round(self.__balance, 2)

    def deposit(self, value: float):
        self.__balance += value

    def withdraw(self, value: float):
        self.__balance -= value

    def get_profit_loss(self):
        return round(self.__balance - self.__initial_balance, 2)
