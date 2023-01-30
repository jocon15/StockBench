from StockBench.indicators.indicators_api import Indicators
import pytest

MACHINE_EPSILON = 0.01


@pytest.fixture
def indicators():
    return Indicators


def test_candle_color(indicators):
    # test lists that don't match in length
    open_data = [1234.5, 1111.9, 3245.62]
    bad_close_data = [1234.5, 1111.9, 3245.62, 2435.23]
    with pytest.raises(Exception):
        indicators.candle_color(open_data, bad_close_data)

    # test lists with asynchronous typing ints/strings
    open_data = [123, '221.4', 560.0]
    close_data = [441.1, 441.1, 441.1]
    result = indicators.candle_color(open_data, close_data)
    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0] == 'green'
    assert result[1] == 'green'
    assert result[2] == 'red'

    # test normal case
    open_data = [134.1, 245.49, 7943.21]
    close_data = [56.97, 42.1, 9424.423]
    result = indicators.candle_color(open_data, close_data)
    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0] == 'red'
    assert result[1] == 'red'
    assert result[2] == 'green'


def test_SMA(indicators):
    # test asynchronous typing ints/strings (<= length)
    close_data = [121, '220.1', 222.2, 555.5, 999.9]
    result = indicators.SMA(5, close_data)
    assert isinstance(result, list)
    assert len(result) == 5
    assert (result[0] - 121.0) < MACHINE_EPSILON
    assert (result[1] - 170.55) < MACHINE_EPSILON
    assert (result[2] - 187.767) < MACHINE_EPSILON
    assert (result[3] - 279.7) < MACHINE_EPSILON
    assert (result[4] - 423.74) < MACHINE_EPSILON

    # test asynchronous typing ints/strings (> length)
    close_data = [222.2, 333.3, 444.4, 555.5, 666.6]
    result = indicators.SMA(3, close_data)
    assert isinstance(result, list)
    assert len(result) == 5
    assert (result[0] - 222.2) < MACHINE_EPSILON
    assert (result[1] - 277.75) < MACHINE_EPSILON
    assert (result[2] - 333.3) < MACHINE_EPSILON
    assert (result[3] - 444.4) < MACHINE_EPSILON
    assert (result[4] - 555.5) < MACHINE_EPSILON


def test_RSI(indicators):
    # test asynchronous typing ints/strings
    close_data = [111.1, 222.2, 333.3, '444.4', 555.5, 666.6, 777.7, 888.8, 999.9,
                  111.1, 222.2, 333.3, 444.4, 555.5, 118.99, 743.2, 987.0, 222.7,
                  345.4, 435.8, 937.4, 266.7, 125.0, 9723.8, 372.7, 736.5, 632]
    result = indicators.RSI(14, close_data)
    assert isinstance(result, list)
    assert len(result) == len(close_data)
    assert (result[14] - 14.359) < MACHINE_EPSILON
    assert (result[15] - 18.515) < MACHINE_EPSILON
    assert (result[16] - 19.177) < MACHINE_EPSILON
    assert (result[17] - 18.416) < MACHINE_EPSILON
    assert (result[18] - 18.495) < MACHINE_EPSILON
    assert (result[19] - 18.354) < MACHINE_EPSILON
