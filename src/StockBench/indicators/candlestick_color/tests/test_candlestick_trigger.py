import os
import sys
import pytest
from unittest.mock import patch

# allows import out a directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from StockBench.indicators.candlestick_color.trigger import CandlestickColorTrigger


@pytest.fixture
def test_object():
    return CandlestickColorTrigger('color')


def test_additional_days(test_object):
    # ============= Arrange ==============

    # ============= Act ==================
    actual = test_object.additional_days('color', {'1': 'red', '0': 'green'})

    # ============= Assert ===============
    assert type(actual) is int
    assert actual == 1


def test_add_to_data(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    try:
        test_object.add_to_data('', '', '', None)
        assert True
    except Exception as e:
        print(e)
        assert False


@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger(data_mocker, test_object):
    # ============= Arrange ==============
    current_day_index = 0

    data_mocker.COLOR = "color"
    data_mocker.get_data_point.side_effect = mock_colors_even

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.check_trigger('color', {'0': 'green', '1': 'red'},
                                     data_mocker,
                                     None,
                                     current_day_index) is True

    assert test_object.check_trigger('color', {'0': 'red', '1': 'green'},
                                     data_mocker,
                                     None,
                                     current_day_index) is False


def mock_colors_even(*args):
    if args[1] % 2 == 0:
        return 'green'
    else:
        return 'red'
