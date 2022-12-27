

class UserAccount:

    def __init__(self, balance: float):
        self.__balance = balance

    def get_balance(self):
        return self.__balance

    def deposit(self, value: float):
        self.__balance += value

    def withdraw(self, value: float):
        self.__balance -= value
