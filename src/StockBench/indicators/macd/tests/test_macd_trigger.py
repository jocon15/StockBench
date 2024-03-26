import os
import sys
import pytest
from unittest.mock import patch
from tests.example_data.ExampleBarsData import EXAMPLE_DATA_MSFT

# allows import from src directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from StockBench.indicators.macd.trigger import MACDTrigger


@pytest.fixture
def test_object():
    return MACDTrigger('MACD')


def test_additional_days(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.additional_days('MACD', '>250') == 26
    assert test_object.additional_days('MACD', '<$price') == 26


@patch('logging.getLogger')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_add_to_data(data_mocker, logger_mocker, test_object):
    # ============= Arrange ==============
    logger_mocker.return_value = logger_mocker
    logger_mocker.warning.side_effect = logger_side_effect
    data_mocker.add_column.side_effect = add_column_side_effect

    # assemble a price list from the example data
    price_data = []
    for day in EXAMPLE_DATA_MSFT['MSFT']:
        price_data.append(float(day['o']))

    data_mocker.get_column_data.return_value = price_data
    data_mocker.get_column_nmes.return_value = []

    # ============= Act ==================
    # test normal case
    test_object.add_to_data('MACD', '>30', 'buy', data_mocker)
    # assertions are done in side effect function

    # ============= Assert ===============
    # assertions are done in side effect function


def add_column_side_effect(*args):
    assert args[0] == 'MACD'
    assert args[1] == [None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       3.285,
                       3.911,
                       3.872,
                       4.081,
                       4.191,
                       3.861,
                       3.345,
                       2.967,
                       2.737,
                       2.419,
                       1.963,
                       1.27,
                       0.417,
                       -0.293,
                       -0.784,
                       -1.19,
                       -0.687,
                       0.343,
                       1.175,
                       1.987,
                       1.808,
                       1.491,
                       1.599,
                       1.61,
                       1.468,
                       1.438,
                       1.203,
                       0.824,
                       0.583,
                       0.288,
                       -0.055,
                       0.117,
                       0.23,
                       0.256,
                       0.306,
                       0.372,
                       0.397,
                       0.381,
                       0.377,
                       0.337,
                       0.397,
                       0.169,
                       -0.149,
                       -0.153,
                       0.01,
                       0.105,
                       0.587,
                       0.855,
                       0.973,
                       1.464,
                       1.866,
                       2.024,
                       2.367,
                       2.757,
                       2.945,
                       2.777,
                       2.68,
                       2.153,
                       1.31,
                       0.784,
                       0.733,
                       0.668,
                       0.452,
                       0.08,
                       -0.062,
                       -0.364,
                       -0.577,
                       -0.422,
                       0.262,
                       0.985,
                       1.703,
                       2.464,
                       3.522,
                       4.121,
                       4.573,
                       4.801,
                       5.423,
                       5.711,
                       6.118,
                       6.332,
                       6.501,
                       6.458,
                       6.6,
                       6.618,
                       6.49,
                       6.403,
                       5.965,
                       5.592,
                       5.393,
                       4.67,
                       3.485,
                       2.491,
                       1.849,
                       1.28,
                       1.169,
                       1.158,
                       0.749,
                       -0.013,
                       -0.388,
                       -0.529,
                       -0.513,
                       -0.166,
                       -0.055,
                       -0.043,
                       0.042,
                       0.214,
                       0.335,
                       0.14,
                       -0.137,
                       -0.412,
                       -0.039,
                       0.27,
                       0.31,
                       0.061,
                       0.262,
                       0.148,
                       0.015,
                       0.354,
                       0.958,
                       1.807,
                       2.468,
                       3.352,
                       4.011,
                       4.655,
                       5.283,
                       5.736,
                       6.067,
                       6.375,
                       6.593,
                       6.52,
                       6.465,
                       6.454,
                       6.182,
                       6.2,
                       6.132,
                       5.586,
                       5.037,
                       4.09,
                       3.593,
                       2.969,
                       2.288,
                       1.527,
                       1.368,
                       1.126,
                       0.407,
                       -0.337,
                       -0.942,
                       -1.112,
                       -1.149,
                       -1.192,
                       -1.767,
                       -1.834,
                       -1.569,
                       -1.327,
                       -0.813,
                       -0.431,
                       -0.135,
                       0.104,
                       0.288,
                       0.177,
                       -0.137,
                       -0.179,
                       -0.045,
                       0.496,
                       0.825,
                       1.083,
                       1.555,
                       1.915,
                       2.323,
                       2.569,
                       2.489,
                       2.664,
                       2.809,
                       3.117]


def logger_side_effect(*args):
    if args[0] == 'Warning: EMA is in incorrect format and will be ignored':
        assert True
    else:
        assert False


@patch('StockBench.indicator.trigger.Trigger.find_single_numeric_in_str')
@patch('StockBench.indicator.trigger.Trigger.find_operator_in_str')
@patch('StockBench.indicator.trigger.Trigger.basic_trigger_check')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger(data_mocker, basic_trigger_mocker, operator_mocker, numeric_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 10
    basic_trigger_mocker.return_value = False
    operator_mocker.return_value = None
    numeric_mocker.return_value = None

    # ============= Act ==================

    # ============= Assert ===============
    # simple trigger not hit case
    assert test_object.check_trigger('MACD', '<6', data_mocker, None, 0) is False

    # simple trigger hit case
    basic_trigger_mocker.return_value = True
    assert test_object.check_trigger('MACD', '>6', data_mocker, None, 0) is True


@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_value_error(data_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 90

    # ============= Act ==================

    # ============= Assert ===============
    # simple trigger not hit case
    try:
        test_object.check_trigger('MACD$slope', '>60', data_mocker, None, 0)
        assert False
    except ValueError:
        assert True


@patch('StockBench.indicator.trigger.Trigger.find_single_numeric_in_str')
@patch('StockBench.indicator.trigger.Trigger.find_operator_in_str')
@patch('StockBench.indicator.trigger.Trigger.basic_trigger_check')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_current_price_symbol_used(data_mocker, basic_trigger_mocker, operator_mocker, numeric_mocker,
                                                 test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.side_effect = data_side_effect
    data_mocker.CLOSE = 'Close'
    basic_trigger_mocker.return_value = False
    operator_mocker.return_value = None
    numeric_mocker.return_value = None

    # ============= Act ==================

    # ============= Assert ===============
    # simple trigger not hit case
    assert test_object.check_trigger('MACD', '>$price', data_mocker, None, 0) is False


def data_side_effect(*args):
    if 'MACD' not in args[0] and 'Close' not in args[0]:
        assert False
    if args[0] == 'close':
        return 100.1
    else:
        return 40.2


def test_check_trigger_2_numbers_present_bad_format(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    # has 2 numbers but does not include slope symbol
    try:
        assert test_object.check_trigger('MACD20ran50', '>$price', None, None, 0)
        assert False
    except ValueError:
        assert True


@patch('StockBench.indicator.trigger.Trigger.find_single_numeric_in_str')
@patch('StockBench.indicator.trigger.Trigger.find_operator_in_str')
@patch('StockBench.indicator.trigger.Trigger.basic_trigger_check')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_slope_used(data_mocker, basic_trigger_mocker, operator_mocker, numeric_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.side_effect = slope_data_side_effect
    basic_trigger_mocker.return_value = False
    operator_mocker.return_value = None
    numeric_mocker.return_value = None

    # ============= Act ==================

    # ============= Assert ===============
    # slope used trigger not hit case
    assert test_object.check_trigger('MACD$slope2', '>1', data_mocker, None, 2) is False

    # slope used trigger hit case
    basic_trigger_mocker.return_value = True
    assert test_object.check_trigger('MACD$slope2', '>1', data_mocker, None, 2) is True


def slope_data_side_effect(*args):
    if 'MACD' not in args[0]:
        assert False
    if args[1] % 2 == 0:
        return 200.0
    else:
        return 100.0
