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

