import os
import sys
from unittest.mock import patch

# allows import out a directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from plugins.ema.trigger import EMATrigger
from tests.example_data.ExampleBarsData import EXAMPLE_DATA_MSFT

# create test object
test_obj = EMATrigger('EMA')


def test_additional_days():
    assert test_obj.additional_days('EMA20') == 20

    assert test_obj.additional_days('EMA50$price') == 50

    assert test_obj.additional_days('EMA50$price') == 50

    assert test_obj.additional_days('EMA20$slope10') == 20

    assert test_obj.additional_days('EMA20$slope30') == 30


@patch('logging.getLogger')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_additional_days(data_mocker, logger_mocker):
    logger_mocker.return_value = logger_mocker
    logger_mocker.warning.side_effect = logger_side_effect

    data_mocker.add_column.side_effect = add_column_side_effect

    # assemble a price list from the example data
    price_data = []
    for day in EXAMPLE_DATA_MSFT['MSFT']:
        price_data.append(float(day['o']))

    data_mocker.get_column_data.return_value = price_data
    data_mocker.get_column_nmes.return_value = []

    # test normal case
    test_obj.add_to_data('EMA20', '>30', 'buy', data_mocker)
    # assertions are done in side effect function

    # test console output if no indicator length is provided
    test_obj.add_to_data('EMA', '>30', 'buy', data_mocker)
    # assertions are done in side effect function


def add_column_side_effect(*args):
    assert args[0] == 'EMA20'
    assert args[1] == [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, 206.932, 207.112, 207.107, 207.431, 207.816, 208.861, 210.152, 211.378,
                       211.909, 212.727, 213.459, 213.682, 213.628, 213.657, 213.802, 213.807, 213.596, 213.032,
                       212.168, 211.342, 210.669, 210.023, 210.404, 211.499, 212.524, 213.658, 213.738, 213.624,
                       213.966, 214.21, 214.273, 214.447, 214.371, 214.086, 213.906, 213.624, 213.24, 213.418, 213.554,
                       213.606, 213.692, 213.805, 213.882, 213.914, 213.957, 213.958, 214.072, 213.853, 213.491,
                       213.454, 213.617, 213.725, 214.31, 214.718, 214.988, 215.722, 216.426, 216.902, 217.621, 218.449,
                       219.095, 219.343, 219.647, 219.42, 218.73, 218.283, 218.321, 218.335, 218.16, 217.766, 217.589,
                       217.201, 216.872, 216.951, 217.689, 218.583, 219.587, 220.756, 222.398, 223.656, 224.831,
                       225.805, 227.281, 228.451, 229.804, 230.987, 232.145, 233.071, 234.207, 235.214, 236.044, 236.9,
                       237.321, 237.748, 238.32, 238.234, 237.481, 236.769, 236.322, 235.865, 235.868, 235.977, 235.613,
                       234.767, 234.267, 233.991, 233.885, 234.182, 234.256, 234.233, 234.302, 234.49, 234.648, 234.449,
                       234.122, 233.755, 234.12, 234.47, 234.549, 234.29, 234.53, 234.426, 234.282, 234.681, 235.451,
                       236.609, 237.676, 239.113, 240.418, 241.806, 243.272, 244.625, 245.898, 247.191, 248.419, 249.33,
                       250.244, 251.198, 251.834, 252.769, 253.601, 253.85, 254.007, 253.601, 253.581, 253.332, 252.918,
                       252.303, 252.288, 252.153, 251.415, 250.536, 249.71, 249.313, 249.055, 248.789, 247.885, 247.501,
                       247.507, 247.532, 247.924, 248.244, 248.523, 248.782, 249.013, 248.922, 248.57, 248.494, 248.622,
                       249.258, 249.727, 250.163, 250.894, 251.565, 252.348, 253.001, 253.301, 253.889, 254.468,
                       255.261]


def logger_side_effect(*args):
    if args[0] == 'Warning: EMA is in incorrect format and will be ignored':
        assert True
    else:
        assert False


# unless you use @patch.multiple, you must patch full path lengths for multiple methods in the same class
@patch('StockBench.triggers.trigger.Trigger.find_numeric_in_str')
@patch('StockBench.triggers.trigger.Trigger.find_operator_in_str')
@patch('StockBench.triggers.trigger.Trigger.basic_triggers_check')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger(data_mocker, basic_trigger_mocker, operator_mocker, numeric_mocker):
    data_mocker.get_data_point.return_value = 10
    basic_trigger_mocker.return_value = False
    operator_mocker.return_value = None
    numeric_mocker.return_value = None

    # simple trigger not hit case
    assert test_obj.check_trigger('EMA20', '>60', data_mocker, None, 0) is False

    # simple trigger hit case
    basic_trigger_mocker.return_value = True
    assert test_obj.check_trigger('EMA20', '>60', data_mocker, None, 0) is True


# unless you use @patch.multiple, you must patch full path lengths for multiple methods in the same class
@patch('StockBench.triggers.trigger.Trigger.find_numeric_in_str')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_value_error(data_mocker, numeric_mocker):
    data_mocker.get_data_point.return_value = 90
    numeric_mocker.side_effect = value_error_side_effect

    # simple trigger not hit case
    assert test_obj.check_trigger('EMA20', '>60', data_mocker, None, 0) is False


def value_error_side_effect(*args):
    raise ValueError()


# unless you use @patch.multiple, you must patch full path lengths for multiple methods in the same class
@patch('StockBench.triggers.trigger.Trigger.find_numeric_in_str')
@patch('StockBench.triggers.trigger.Trigger.find_operator_in_str')
@patch('StockBench.triggers.trigger.Trigger.basic_triggers_check')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_current_price_symbol_used(data_mocker, basic_trigger_mocker, operator_mocker, numeric_mocker):
    data_mocker.get_data_point.side_effect = data_side_effect
    basic_trigger_mocker.return_value = False
    operator_mocker.return_value = None
    numeric_mocker.return_value = None

    # simple trigger not hit case
    assert test_obj.check_trigger('EMA20', '>$price', data_mocker, None, 0) is False


def data_side_effect(*args):
    if args[0] == 'close':
        return 100.1
    else:
        return 40.2


def test_check_trigger_2_numbers_present_bad_format():
    # has 2 numbers but does not include slope symbol
    assert test_obj.check_trigger('EMA20ran50', '>$price', None, None, 0) is False


@patch('StockBench.triggers.trigger.Trigger.find_numeric_in_str')
@patch('StockBench.triggers.trigger.Trigger.find_operator_in_str')
@patch('StockBench.triggers.trigger.Trigger.basic_triggers_check')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_slope_used(data_mocker, basic_trigger_mocker, operator_mocker, numeric_mocker):
    data_mocker.get_data_point.side_effect = slope_data_side_effect
    basic_trigger_mocker.return_value = False
    operator_mocker.return_value = None
    numeric_mocker.return_value = None

    # slope used trigger not hit case
    assert test_obj.check_trigger('EMA20$slope1', '>50', data_mocker, None, 2) is False

    # slope used trigger hit case
    basic_trigger_mocker.return_value = True
    assert test_obj.check_trigger('EMA20$slope1', '>50', data_mocker, None, 2) is True


def slope_data_side_effect(*args):
    if args[1] % 2 == 0:
        return 200.0
    else:
        return 100.0


@patch('StockBench.triggers.trigger.Trigger.find_numeric_in_str')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_slope_value_error(data_mocker, numeric_mocker):
    data_mocker.get_data_point.return_value = 90
    numeric_mocker.side_effect = value_error_side_effect

    # simple trigger not hit case
    assert test_obj.check_trigger('EMA20$slope', '>60', data_mocker, None, 0) is False
