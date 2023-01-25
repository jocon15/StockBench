from StockBench.accounting.user_account import UserAccount

import pytest

"""
Look up code coverage https://coverage.readthedocs.io/en/7.1.0/
"""

# ======= CONSTANTS ======
MACHINE_EPSILON = 0.001


@pytest.fixture
def user_account():
    # sets up an instance of UserAccount to use across functions
    return UserAccount(1000.0)


def test_deposit(user_account):
    # test deposit $100.0 as a float
    user_account.deposit(100.0)
    assert (user_account.get_balance() - 1100.0) < MACHINE_EPSILON

    # test deposit $100 as an integer
    user_account.deposit(100)
    assert (user_account.get_balance() - 1200.0) < MACHINE_EPSILON


def test_withdraw(user_account):
    pass
