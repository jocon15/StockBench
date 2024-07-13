from StockBench.account.user_account import UserAccount


def test_deposit():
    # ============= Arrange ==============
    test_object = UserAccount(1000.0)

    # ============= Act ==================
    # ensure initial expected amount
    assert int(test_object.get_balance()) == 1000

    test_object.deposit(100.0)

    actual = test_object.get_balance()

    # ============= Assert ===============
    assert int(actual) == 1100


def test_withdraw():
    # ============= Arrange ==============
    test_object = UserAccount(1000.0)

    # ============= Act ==================
    test_object.withdraw(100.0)

    actual = test_object.get_balance()

    # ============= Assert ===============
    assert int(actual) == 900


def test_get_initial_balance():
    # ============= Arrange ==============
    test_object = UserAccount(1000.0)

    # ============= Act ==================
    test_object.withdraw(200.0)

    actual = test_object.get_initial_balance()

    # ============= Assert ===============
    assert type(actual) is float
    assert int(actual) == 1000

def test_get_balance():
    # ============= Arrange ==============
    test_object = UserAccount(1000.0)

    # ============= Act ==================
    test_object.withdraw(200.0)

    actual = test_object.get_balance()

    # ============= Assert ===============
    assert type(actual) is float
    assert int(actual) == 800


def test_get_profit_loss():
    # ============= Arrange ==============
    test_object = UserAccount(1000.0)

    # ============= Act ==================
    test_object.deposit(582.0)

    actual = test_object.get_profit_loss()

    # ============= Assert ===============
    assert type(actual) is float
    assert int(actual) == 582
