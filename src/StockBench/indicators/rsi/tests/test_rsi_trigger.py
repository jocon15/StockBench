import os
import sys
import pytest
from unittest.mock import patch
from tests.example_data.ExampleBarsData import EXAMPLE_DATA_MSFT

# allows import out a directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from StockBench.indicators.rsi.trigger import RSITrigger


@pytest.fixture
def test_object():
    return RSITrigger('RSI')


@patch('StockBench.simulation_data.data_manager.DataManager')
def test_additional_days(data_mocker, test_object):
    data_mocker.get_data_length.return_value = 200

    assert test_object.additional_days('RSI', '>20') == 14

    assert test_object.additional_days('RSI50', '>20') == 50

    assert test_object.additional_days('RSI50$price', '>20') == 50

    assert test_object.additional_days('RSI20$slope10', '>20') == 20

    assert test_object.additional_days('RSI20$slope30', '>20') == 30


@patch('logging.getLogger')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_add_to_data(data_mocker, logger_mocker, test_object):
    logger_mocker.return_value = logger_mocker
    logger_mocker.warning.side_effect = logger_side_effect

    data_mocker.add_column.side_effect = add_column_side_effect

    # assemble a price list from the example data
    price_data = []
    for day in EXAMPLE_DATA_MSFT['MSFT']:
        price_data.append(float(day['o']))

    data_mocker.get_column_data.return_value = price_data
    data_mocker.get_column_names.return_value = []
    data_mocker.get_data_length.return_value = 200

    # test normal case
    test_object.add_to_data('RSI', '>30', 'buy', data_mocker)
    # assertions are done in side effect function


def add_column_side_effect(*args):
    if args[0] == 'RSI':
        assert args[1] == [0,
                       0,
                       11.34,
                       25.734,
                       30.071,
                       34.705,
                       37.611,
                       35.494,
                       31.06,
                       30.591,
                       31.379,
                       36.701,
                       35.833,
                       35.011,
                       35.022,
                       37.471,
                       40.224,
                       42.559,
                       43.486,
                       43.552,
                       45.78,
                       44.317,
                       45.827,
                       45.535,
                       44.052,
                       45.69,
                       46.79,
                       44.915,
                       44.342,
                       44.053,
                       45.998,
                       45.948,
                       48.408,
                       47.752,
                       47.024,
                       48.805,
                       49.136,
                       52.526,
                       53.582,
                       58.26,
                       54.55,
                       55.394,
                       59.18,
                       61.074,
                       57.774,
                       55.913,
                       50.62,
                       52.683,
                       54.36,
                       54.409,
                       54.472,
                       53.284,
                       55.658,
                       54.204,
                       54.125,
                       56.397,
                       57.342,
                       56.348,
                       57.141,
                       58.3,
                       56.415,
                       56.268,
                       59.317,
                       62.393,
                       60.284,
                       60.344,
                       60.591,
                       57.743,
                       66.253,
                       67.309,
                       68.027,
                       69.861,
                       66.973,
                       66.213,
                       66.998,
                       65.172,
                       65.214,
                       66.23,
                       66.811,
                       64.821,
                       66.51,
                       63.347,
                       63.039,
                       58.249,
                       53.251,
                       54.107,
                       53.392,
                       53.907,
                       52.317,
                       50.486,
                       51.683,
                       50.055,
                       49.944,
                       52.79,
                       56.566,
                       56.161,
                       56.146,
                       54.646,
                       55.289,
                       56.083,
                       56.058,
                       56.702,
                       58.634,
                       57.582,
                       58.282,
                       58.955,
                       59.005,
                       58.813,
                       59.503,
                       60.689,
                       60.881,
                       58.901,
                       58.75,
                       57.904,
                       58.931,
                       58.058,
                       56.475,
                       56.395,
                       55.253,
                       56.364,
                       54.673,
                       53.807,
                       51.95,
                       49.76,
                       50.273,
                       49.658,
                       46.184,
                       49.026,
                       49.269,
                       49.255,
                       45.139,
                       43.608,
                       44.737,
                       42.562,
                       42.392,
                       42.051,
                       47.188,
                       44.954,
                       43.912,
                       44.061,
                       46.975,
                       48.917,
                       53.856,
                       57.2,
                       58.588,
                       60.113,
                       57.769,
                       59.935,
                       58.424,
                       58.605,
                       59.001,
                       56.728,
                       56.455,
                       56.555,
                       51.888,
                       50.436,
                       51.009,
                       48.09,
                       46.699,
                       45.142,
                       48.904,
                       49.017,
                       50.19,
                       46.163,
                       45.573,
                       43.878,
                       45.048,
                       44.324,
                       45.09,
                       44.706,
                       42.024,
                       42.837,
                       44.937,
                       47.863,
                       44.571,
                       44.709,
                       41.437,
                       45.153,
                       46.321,
                       44.794,
                       47.487,
                       48.814,
                       48.835,
                       48.516,
                       52.373,
                       50.518,
                       52.772,
                       53.522,
                       54.511,
                       57.334,
                       58.378,
                       57.66,
                       57.521,
                       55.249,
                       52.502,
                       53.704,
                       53.243,
                       52.976,
                       52.535,
                       51.143]
    elif args[0] == 'RSI_lower':
        assert args[1] == [30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0]
    elif args[0] == 'RSI_upper':
        assert args[1] == [30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0,
 30.0]
    else:
        assert False


def logger_side_effect(*args):
    if args[0] == 'Warning: RSI is in incorrect format and will be ignored':
        assert True
    else:
        assert False
        
        
@patch('StockBench.trigger.trigger.Trigger.find_single_numeric_in_str')
@patch('StockBench.trigger.trigger.Trigger.find_operator_in_str')
@patch('StockBench.trigger.trigger.Trigger.basic_trigger_check')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger(data_mocker, basic_trigger_mocker, operator_mocker, numeric_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 10
    basic_trigger_mocker.return_value = False
    operator_mocker.return_value = None
    numeric_mocker.return_value = None

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.check_trigger('RSI', '>60', data_mocker, None, 0) is False

    assert test_object.check_trigger('RSI', '>60', data_mocker, None, 0) is False


@patch('StockBench.trigger.trigger.Trigger.find_single_numeric_in_str')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_value_error(data_mocker, numeric_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 90

    # ============= Act ==================

    # ============= Assert ===============
    # simple trigger not hit case
    try:
        assert test_object.check_trigger('12RSI12', '>60', data_mocker, None, 0)
        assert False
    except ValueError:
        assert True


# unless you use @patch.multiple, you must patch full path lengths for multiple methods in the same class
@patch('StockBench.trigger.trigger.Trigger.find_single_numeric_in_str')
@patch('StockBench.trigger.trigger.Trigger.find_operator_in_str')
@patch('StockBench.trigger.trigger.Trigger.basic_trigger_check')
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
    assert test_object.check_trigger('RSI20', '>$price', data_mocker, None, 0) is False


def data_side_effect(*args):
    if 'RSI' not in args[0] and 'Close' not in args[0]:
        assert False
    if args[0] == 'close':
        return 100.1
    else:
        return 40.2


@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_2_numbers_present_bad_format(data_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.side_effect = data_side_effect
    data_mocker.CLOSE = 'Close'

    # ============= Act ==================

    # ============= Assert ===============
    # has 2 numbers but does not include slope symbol
    assert test_object.check_trigger('RSIran50', '>$price', data_mocker, None, 0) is False


@patch('StockBench.trigger.trigger.Trigger.find_single_numeric_in_str')
@patch('StockBench.trigger.trigger.Trigger.find_operator_in_str')
@patch('StockBench.trigger.trigger.Trigger.basic_trigger_check')
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
    assert test_object.check_trigger('RSI$slope2', '>50', data_mocker, None, 2) is False

    # slope used trigger hit case
    basic_trigger_mocker.return_value = True
    assert test_object.check_trigger('RSI$slope2', '>50', data_mocker, None, 2) is True


def slope_data_side_effect(*args):
    if 'RSI' not in args[0]:
        assert False
    if args[1] % 2 == 0:
        return 200.0
    else:
        return 100.0


@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_slope_value_error(data_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 90

    # ============= Act ==================

    # ============= Assert ===============
    # simple trigger not hit case
    try:
        assert test_object.check_trigger('RSI$slope', '>60', data_mocker, None, 0) is False
        assert False
    except ValueError:
        assert True
