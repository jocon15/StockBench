import os
import sys
import pytest
from unittest.mock import patch
from tests.example_data.ExampleBarsData import EXAMPLE_DATA_MSFT

# allows import out a directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


from StockBench.indicators.sma.trigger import SMATrigger


@pytest.fixture
def test_object():
    return SMATrigger('SMA')


def test_additional_days(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.additional_days('SMA20', '>20') == 20
    assert type(test_object.additional_days('SMA20', '>20')) is int
    assert test_object.additional_days('SMA50$price', '>20') == 50
    assert test_object.additional_days('SMA50$price', '>20') == 50
    assert test_object.additional_days('SMA20$slope10', '>20') == 20
    assert test_object.additional_days('SMA20$slope30', '>20') == 30


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
    test_object.add_to_data('SMA20', '>30', 'buy', data_mocker)
    # assertions are done in side effect function

    # test console output if no indicator length is provided
    test_object.add_to_data('SMA20', '>30', 'buy', data_mocker)

    # ============= Assert ===============
    # assertions are done in side effect function


def add_column_side_effect(*args):
    assert args[0] == 'SMA20'
    assert args[1] == [215.1, 210.8, 209.733, 210.415, 209.772, 208.85, 208.789, 209.017, 208.021, 207.499, 206.562,
                       206.437, 206.549, 206.071, 205.903, 206.218, 206.402, 206.476, 206.841, 206.899, 206.507,
                       206.623, 206.596, 206.499, 206.712, 207.44, 208.14, 208.76, 209.605, 210.49, 211.651, 212.189,
                       212.45, 213.154, 213.735, 213.88, 213.992, 213.989, 213.517, 213.291, 213.142, 212.896, 213.244,
                       213.813, 214.352, 214.635, 214.239, 213.714, 213.727, 213.529, 213.251, 213.266, 213.293,
                       213.165, 213.016, 212.871, 212.771, 213.143, 213.688, 214.218, 214.73, 215.279, 215.309, 214.925,
                       214.53, 214.007, 214.04, 214.001, 213.643, 213.472, 213.487, 213.419, 213.73, 214.091, 214.358,
                       214.945, 215.621, 215.937, 216.417, 217.027, 217.563, 217.904, 218.3, 218.452, 218.342, 218.346,
                       218.522, 218.857, 219.179, 219.225, 219.262, 219.201, 218.895, 218.851, 219.208, 219.428,
                       219.728, 220.25, 220.928, 221.393, 221.93, 222.599, 223.537, 224.653, 226.177, 227.587, 228.81,
                       229.98, 231.405, 232.943, 234.344, 235.92, 237.298, 238.503, 239.456, 239.973, 240.033, 239.94,
                       239.644, 239.44, 239.436, 239.533, 239.076, 238.434, 237.777, 237.234, 236.72, 236.477, 235.975,
                       235.436, 234.988, 234.55, 234.292, 233.83, 233.193, 232.836, 233.199, 233.588, 233.749, 233.764,
                       233.81, 233.631, 233.669, 234.256, 234.918, 235.731, 236.477, 237.265, 238.158, 239.207, 240.319,
                       241.379, 242.471, 243.816, 245.27, 246.655, 247.722, 248.846, 249.975, 251.466, 252.701, 253.84,
                       254.969, 255.533, 256.064, 256.232, 256.29, 255.975, 255.942, 255.736, 255.096, 254.332, 253.525,
                       252.828, 252.154, 251.568, 250.587, 249.766, 249.25, 248.556, 248.063, 247.816, 247.6, 247.674,
                       247.566, 247.42, 247.233, 247.298, 247.183, 247.404, 247.893, 248.499, 249.298, 249.917, 250.577,
                       251.224, 252.066, 252.848, 253.469, 254.22]


def logger_side_effect(*args):
    if args[0] == 'Warning: SMA is in incorrect format and will be ignored':
        assert True
    else:
        assert False


@patch('StockBench.triggers.trigger.Trigger.find_numeric_in_str')
@patch('StockBench.triggers.trigger.Trigger.find_operator_in_str')
@patch('StockBench.triggers.trigger.Trigger.basic_triggers_check')
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
    assert test_object.check_trigger('SMA20', '>60', data_mocker, None, 0) is False

    # simple trigger hit case
    basic_trigger_mocker.return_value = True
    assert test_object.check_trigger('SMA20', '>60', data_mocker, None, 0) is True


# unless you use @patch.multiple, you must patch full path lengths for multiple methods in the same class
@patch('StockBench.triggers.trigger.Trigger.find_numeric_in_str')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_value_error(data_mocker, numeric_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 90
    numeric_mocker.side_effect = value_error_side_effect

    # ============= Act ==================

    # ============= Assert ===============
    # simple trigger not hit case
    assert test_object.check_trigger('SMA20', '>60', data_mocker, None, 0) is False


def value_error_side_effect(*args):  # noqa
    raise ValueError()


# unless you use @patch.multiple, you must patch full path lengths for multiple methods in the same class
@patch('StockBench.triggers.trigger.Trigger.find_numeric_in_str')
@patch('StockBench.triggers.trigger.Trigger.find_operator_in_str')
@patch('StockBench.triggers.trigger.Trigger.basic_triggers_check')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_current_price_symbol_used(data_mocker, basic_trigger_mocker, operator_mocker, numeric_mocker,
                                                 test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.side_effect = data_side_effect
    basic_trigger_mocker.return_value = False
    operator_mocker.return_value = None
    numeric_mocker.return_value = None

    # ============= Act ==================

    # ============= Assert ===============
    # simple trigger not hit case
    assert test_object.check_trigger('SMA20', '>$price', data_mocker, None, 0) is False


def data_side_effect(*args):
    if args[0] == 'close':
        return 100.1
    else:
        return 40.2


def test_check_trigger_2_numbers_present_bad_format(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    # has 2 numbers but does not include slope symbol
    assert test_object.check_trigger('SMA20ran50', '>$price', None, None, 0) is False


@patch('StockBench.triggers.trigger.Trigger.find_numeric_in_str')
@patch('StockBench.triggers.trigger.Trigger.find_operator_in_str')
@patch('StockBench.triggers.trigger.Trigger.basic_triggers_check')
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
    assert test_object.check_trigger('SMA20$slope2', '>50', data_mocker, None, 2) is False

    # slope used trigger hit case
    basic_trigger_mocker.return_value = True
    assert test_object.check_trigger('SMA20$slope2', '>50', data_mocker, None, 2) is True


def slope_data_side_effect(*args):
    if args[1] % 2 == 0:
        return 200.0
    else:
        return 100.0


@patch('StockBench.triggers.trigger.Trigger.find_numeric_in_str')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_slope_value_error(data_mocker, numeric_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 90
    numeric_mocker.side_effect = value_error_side_effect

    # ============= Act ==================

    # ============= Assert ===============
    # simple trigger not hit case
    assert test_object.check_trigger('SMA20$slope', '>60', data_mocker, None, 0) is False
