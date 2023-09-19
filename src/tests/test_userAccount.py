from StockBench.account.user_account import UserAccount
from StockBench.constants import FLOAT_COMPARISON_EPSILON
import pytest

"""
Look up code coverage https://coverage.readthedocs.io/en/7.1.0/
"""


@pytest.fixture
def user_account():
    # sets up an instance of UserAccount to use across functions
    return UserAccount(1000.0)


def test_deposit(user_account):
    # test deposit $100.0 as a float
    user_account.deposit(100.0)
    assert (user_account.get_balance() - 1100.0) < FLOAT_COMPARISON_EPSILON

    # test deposit $100 as an integer
    user_account.deposit(100)
    assert (user_account.get_balance() - 1200.0) < FLOAT_COMPARISON_EPSILON


def test_withdraw(user_account):
    # test deposit $100.0 as a float
    user_account.withdraw(100.0)
    assert (user_account.get_balance() - 1100.0) < FLOAT_COMPARISON_EPSILON

    # test deposit $100 as an integer
    user_account.withdraw(100)
    assert (user_account.get_balance() - 1000.0) < FLOAT_COMPARISON_EPSILON


def test_get_balance(user_account):
    # gets tested twice in test_deposit() and test_withdraw()
    assert (user_account.get_balance() - 1000.0) < FLOAT_COMPARISON_EPSILON


def test_get_profit_loss(user_account):
    # balance and initial balance are the same at this point
    assert (user_account.get_balance() - 1000.0) < FLOAT_COMPARISON_EPSILON

    # change the balance
    user_account.deposit(1234.18)
    assert (user_account.get_profit_loss() - 1234.18) < FLOAT_COMPARISON_EPSILON
