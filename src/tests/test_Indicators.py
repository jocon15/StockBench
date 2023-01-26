from StockBench.indicators.indicators_api import Indicators
import pytest

MACHINE_EPSILON = 0.001


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

    # test normal case

    open_colors = ['red', 'green', 'red']
    close_data = []
