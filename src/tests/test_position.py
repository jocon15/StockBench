from StockBench.position.position import Position


def test_close_position():
    # ============= Arrange ==============
    test_object = Position(150.0, 2, 1, 'SMA20 > 100')
    # make sure the test_object has not been closed yet

    # ============= Act ==================
    # ensure sell price is None as expected
    assert test_object.get_sell_price() is None
    test_object.close_position(200.0, 2, 'red red')
    
    actual = test_object.get_sell_price()

    # ============= Assert ===============
    assert type(actual) is float
    assert int(actual) == 200


def test_profit_loss():
    # ============= Arrange ==============
    test_object = Position(150.0, 2, 1, 'SMA20 > 100')

    # ============= Act ==================
    actual = test_object.profit_loss(200.0)

    # ============= Assert ===============
    assert type(actual) is float
    assert int(actual) == 100


def test_intraday_profit_loss():
    # ============= Arrange ==============
    test_object = Position(150.0, 2, 1, 'SMA20 > 100')

    # ============= Act ==================
    actual = test_object.intraday_profit_loss(100, 200)

    # ============= Assert ===============
    assert type(actual) is float
    assert int(actual) == 200


def test_lifetime_profit_loss():
    # ============= Arrange ==============
    test_object = Position(150.0, 2, 1, 'SMA20 > 100')

    # ============= Act ==================
    test_object.close_position(200.0, 2, 'red red')

    actual = test_object.lifetime_profit_loss()

    # ============= Assert ===============
    assert type(actual) is float
    assert int(actual) == 100


def test_profit_loss_percent():
    # ============= Arrange ==============
    test_object = Position(150.0, 2, 1, 'SMA20 > 100')

    # ============= Act ==================
    test_object.close_position(200.0, 2, 'red red')

    actual = test_object.profit_loss_percent(200)

    # ============= Assert ===============
    assert type(actual) is float
    assert int(actual) == 33


def test_intraday_profit_loss_percent():
    # ============= Arrange ==============
    test_object = Position(150.0, 2, 1, 'SMA20 > 100')

    # ============= Act ==================
    actual = test_object.intraday_profit_loss_percent(100, 200)

    # ============= Assert ===============
    assert type(actual) is float
    assert int(actual) == 100


def test_lifetime_profit_loss_percent():
    # ============= Arrange ==============
    test_object = Position(150.0, 2, 1, 'SMA20 > 100')

    # ============= Act ==================
    # ensure sell price is None as expected
    assert test_object.get_sell_price() is None
    test_object.close_position(200.0, 2, 'red red')
    actual = test_object.lifetime_profit_loss_percent()

    # ============= Assert ===============
    assert type(actual) is float
    assert int(actual) == 33


def test_get_buy_price():
    # ============= Arrange ==============
    test_object = Position(150.0, 2, 1, 'SMA20 > 100')

    # ============= Act ==================
    actual = test_object.get_buy_price()

    # ============= Assert ===============
    assert type(actual) is float
    assert int(actual) == 150


def test_get_share_count():
    # ============= Arrange ==============
    test_object = Position(150.0, 2, 1, 'SMA20 > 100')

    # ============= Act ==================
    actual = test_object.get_share_count()

    # ============= Assert ===============
    assert type(actual) is float
    assert int(actual) == 2


def test_get_sell_price():
    # ============= Arrange ==============
    test_object = Position(150.0, 2, 1, 'SMA20 > 100')

    # ============= Act ==================
    # ensure the sell price is None as expected
    assert test_object.get_sell_price() is None

    test_object.close_position(200.0, 2, 'red red')

    actual = test_object.get_sell_price()

    # ============= Assert ===============
    assert type(actual) is float
    assert int(actual) == 200
