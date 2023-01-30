from StockBench.position.position_obj import Position
import pytest

MACHINE_EPSILON = 0.01


@pytest.fixture
def position():
    return Position(150.0, 2)


def test_close_position():
    # create a position
    position = Position(150.0, 2)
    # make sure the position has not been closed yet
    assert position.get_sell_price() is None
    # close the position (int/string
    position.close_position(200)
    assert (position.get_sell_price() - 200.0) < MACHINE_EPSILON

    # create a position
    position = Position(150.0, 2)
    # normal close
    position.close_position(200.0)


def test_profit_loss():
    # create a position
    position = Position(150.0, 2)
    # ensure accurate profit/loss calculation
    assert (position.profit_loss(200.0) - 100.0) < MACHINE_EPSILON


def test_lifetime_profit_loss():
    # create a position
    position = Position(150.0, 2)
    # liquidate the position
    position.close_position(200.0)
    # ensure accurate profit/loss calculation
    assert (position.lifetime_profit_loss() - 100.0) < MACHINE_EPSILON


def test_get_buy_price():
    # create a position
    position = Position(150.0, 2)
    # ensure accuracy of buy price
    assert (position.get_buy_price() - 150.0) < MACHINE_EPSILON


def test_get_share_count():
    # create a position
    position = Position(150.0, 2)
    # ensure accuracy of the share count
    assert (position.get_share_count() - 2.0) < MACHINE_EPSILON


def test_get_sell_price():
    # create a position
    position = Position(150.0, 2)
    # ensure the initial sell price is None
    assert position.get_sell_price() is None
    # liquidate the position
    position.close_position(200.0)
    # ensure the accuracy of the sell price
    assert (position.get_sell_price() - 200.0) < MACHINE_EPSILON
