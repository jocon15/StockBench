import pytest
from unittest.mock import patch
from tests.example_data.ExampleBarsData import EXAMPLE_DATA_MSFT
from StockBench.indicators.macd.trigger import MACDTrigger
from StockBench.controllers.indicator import StrategyIndicatorError


@pytest.fixture
def test_object():
    return MACDTrigger('MACD')


def test_additional_days_from_rule_key(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.calculate_additional_days_from_rule_key('MACD', None) == 26
    assert test_object.calculate_additional_days_from_rule_key('MACD', None) == 26


def test_additional_days_from_rule_value(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.calculate_additional_days_from_rule_value('<MACD') == 26
    assert test_object.calculate_additional_days_from_rule_value('>MACD') == 26


@patch('logging.getLogger')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_add_to_data_from_rule_key(data_mocker, logger_mocker, test_object):
    # ============= Arrange ==============
    logger_mocker.return_value = logger_mocker
    logger_mocker.warning.side_effect = logger_side_effect
    data_mocker.add_column.side_effect = add_column_side_effect

    # assemble a price list from the example data
    price_data = []
    for day in EXAMPLE_DATA_MSFT['MSFT']:
        price_data.append(float(day['c']))

    data_mocker.get_column_data.return_value = price_data
    data_mocker.get_column_nmes.return_value = []

    # ============= Act ==================
    # test normal case
    test_object.add_indicator_data_from_rule_key('MACD', '>30', 'buy', data_mocker)
    # assertions are done in side effect function

    # ============= Assert ===============
    # assertions are done in side effect function


@patch('logging.getLogger')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_add_to_data_from_rule_value(data_mocker, logger_mocker, test_object):
    # ============= Arrange ==============
    logger_mocker.return_value = logger_mocker
    logger_mocker.warning.side_effect = logger_side_effect
    data_mocker.add_column.side_effect = add_column_side_effect

    # assemble a price list from the example data
    price_data = []
    for day in EXAMPLE_DATA_MSFT['MSFT']:
        price_data.append(float(day['c']))

    data_mocker.get_column_data.return_value = price_data
    data_mocker.get_column_nmes.return_value = []

    # ============= Act ==================
    # test normal case
    test_object.add_indicator_data_from_rule_value('MACD', '>30', data_mocker)
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
                       4.228,
                       4.541,
                       4.633,
                       4.652,
                       4.182,
                       3.791,
                       3.46,
                       3.165,
                       3.011,
                       2.369,
                       2.078,
                       0.994,
                       0.268,
                       -0.449,
                       -1.026,
                       -1.164,
                       -0.445,
                       0.679,
                       1.578,
                       1.844,
                       1.447,
                       1.549,
                       1.537,
                       1.657,
                       1.739,
                       1.55,
                       1.105,
                       0.851,
                       0.485,
                       0.173,
                       0.227,
                       0.258,
                       0.402,
                       0.427,
                       0.599,
                       0.664,
                       0.615,
                       0.581,
                       0.541,
                       0.636,
                       0.338,
                       0.029,
                       0.007,
                       0.063,
                       0.103,
                       0.535,
                       0.886,
                       1.05,
                       1.519,
                       1.981,
                       2.085,
                       2.277,
                       2.581,
                       2.736,
                       2.618,
                       2.551,
                       2.106,
                       1.749,
                       0.987,
                       0.864,
                       0.858,
                       0.68,
                       0.328,
                       0.166,
                       -0.233,
                       -0.578,
                       -0.534,
                       0.124,
                       0.695,
                       1.21,
                       1.894,
                       2.652,
                       3.256,
                       4.158,
                       4.249,
                       4.893,
                       5.333,
                       5.893,
                       6.181,
                       6.36,
                       6.45,
                       6.553,
                       6.48,
                       6.485,
                       6.458,
                       6.256,
                       6.071,
                       5.819,
                       5.335,
                       4.382,
                       3.479,
                       2.834,
                       1.84,
                       1.309,
                       1.257,
                       0.956,
                       0.206,
                       -0.436,
                       -0.561,
                       -0.984,
                       -0.805,
                       -0.758,
                       -0.324,
                       -0.097,
                       0.003,
                       0.311,
                       0.509,
                       0.142,
                       -0.212,
                       0.002,
                       0.288,
                       0.345,
                       0.135,
                       0.3,
                       0.329,
                       0.109,
                       0.227,
                       0.833,
                       1.831,
                       2.497,
                       3.151,
                       3.897,
                       4.641,
                       5.182,
                       5.749,
                       5.922,
                       6.281,
                       6.585,
                       6.606,
                       6.492,
                       6.515,
                       6.187,
                       6.173,
                       6.126,
                       6.069,
                       5.359,
                       4.562,
                       3.87,
                       3.253,
                       2.418,
                       1.623,
                       1.237,
                       1.129,
                       0.628,
                       0.145,
                       -0.809,
                       -1.24,
                       -1.144,
                       -1.292,
                       -1.565,
                       -1.752,
                       -1.613,
                       -1.588,
                       -1.098,
                       -0.623,
                       -0.271,
                       -0.136,
                       -0.021,
                       -0.123,
                       -0.206,
                       -0.398,
                       -0.139,
                       0.312,
                       0.555,
                       0.825,
                       1.317,
                       1.739,
                       2.209,
                       2.443,
                       2.518,
                       2.82,
                       2.897,
                       3.189,
                       3.534]


def logger_side_effect(*args):
    if args[0] == 'Warning: EMA is in incorrect format and will be ignored':
        assert True
    else:
        assert False


@patch('StockBench.simulation_data.data_manager.DataManager')
def test_get_value_when_referenced(data_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 234.5

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.get_indicator_value_when_referenced('>=MACD', data_mocker, 25) == 234.5


@patch('StockBench.algorithm.algorithm.Trigger.find_single_numeric_in_str')
@patch('StockBench.algorithm.algorithm.Trigger.find_operator_in_str')
@patch('StockBench.algorithm.algorithm.Trigger.basic_trigger_check')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger(data_mocker, basic_trigger_mocker, operator_mocker, numeric_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 10
    basic_trigger_mocker.return_value = False
    operator_mocker.return_value = None
    numeric_mocker.return_value = None

    # ============= Act ==================

    # ============= Assert ===============
    # simple algorithm not hit case
    assert test_object.check_trigger('MACD', '<6', data_mocker, None, 0) is False  # noqa

    # simple algorithm hit case
    basic_trigger_mocker.return_value = True
    assert test_object.check_trigger('MACD', '>6', data_mocker, None, 0) is True  # noqa


@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_value_error(data_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 90

    # ============= Act ==================

    # ============= Assert ===============
    # simple algorithm not hit case
    try:
        test_object.check_trigger('MACD$slope', '>60', data_mocker, None, 0)  # noqa
        assert False
    except StrategyIndicatorError:
        assert True


@patch('StockBench.algorithm.algorithm.Trigger.find_single_numeric_in_str')
@patch('StockBench.algorithm.algorithm.Trigger.find_operator_in_str')
@patch('StockBench.algorithm.algorithm.Trigger.basic_trigger_check')
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
    # simple algorithm not hit case
    assert test_object.check_trigger('MACD', '>20', data_mocker, None, 0) is False  # noqa


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
        assert test_object.check_trigger('MACD20ran50', '>20', None, None, 0)  # noqa
        assert False
    except StrategyIndicatorError:
        assert True


@patch('StockBench.algorithm.algorithm.Trigger.find_single_numeric_in_str')
@patch('StockBench.algorithm.algorithm.Trigger.find_operator_in_str')
@patch('StockBench.algorithm.algorithm.Trigger.basic_trigger_check')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_slope_used(data_mocker, basic_trigger_mocker, operator_mocker, numeric_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.side_effect = slope_data_side_effect
    basic_trigger_mocker.return_value = False
    operator_mocker.return_value = None
    numeric_mocker.return_value = None

    # ============= Act ==================

    # ============= Assert ===============
    # slope used algorithm not hit case
    assert test_object.check_trigger('MACD$slope2', '>1', data_mocker, None, 2) is False  # noqa

    # slope used algorithm hit case
    basic_trigger_mocker.return_value = True
    assert test_object.check_trigger('MACD$slope2', '>1', data_mocker, None, 2) is True  # noqa


def slope_data_side_effect(*args):
    if 'MACD' not in args[0]:
        assert False
    if args[1] % 2 == 0:
        return 200.0
    else:
        return 100.0
