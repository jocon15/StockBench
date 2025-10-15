import pytest
from unittest.mock import patch
from tests.example_data.ExampleBarsData import EXAMPLE_DATA_MSFT
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager
from StockBench.controllers.simulator.indicators.stochastic.trigger import StochasticTrigger
from StockBench.controllers.simulator.indicator import StrategyIndicatorError


@pytest.fixture
def test_object():
    return StochasticTrigger('stochastic')


def test_additional_days_from_rule_key(test_object):
    assert test_object.calculate_additional_days_from_rule_key('stochastic', None) == 14
    assert test_object.calculate_additional_days_from_rule_key('stochastic20', None) == 20
    assert test_object.calculate_additional_days_from_rule_key('stochastic20$slope10', None) == 20
    assert test_object.calculate_additional_days_from_rule_key('stochastic20$slope30', None) == 30


def test_additional_days_from_rule_value(test_object):
    assert test_object.calculate_additional_days_from_rule_value('stochastic') == 14
    assert test_object.calculate_additional_days_from_rule_value('stochastic20') == 20
    assert test_object.calculate_additional_days_from_rule_value('stochastic20$slope10') == 20
    assert test_object.calculate_additional_days_from_rule_value('stochastic20$slope30') == 30


@patch('logging.getLogger')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_add_to_data_rule_key(data_mocker, logger_mocker, test_object):
    logger_mocker.return_value = logger_mocker
    logger_mocker.warning.side_effect = logger_side_effect

    data_mocker.add_column.side_effect = add_column_side_effect

    # assemble a price list from the example data
    price_data = []
    for day in EXAMPLE_DATA_MSFT['MSFT']:
        price_data.append(float(day['c']))

    data_mocker.HIGH = DataManager.HIGH
    data_mocker.LOW = DataManager.LOW
    data_mocker.CLOSE = DataManager.CLOSE

    data_mocker.get_column_data.side_effect = get_column_data_side_effect
    data_mocker.get_column_names.return_value = []
    data_mocker.get_data_length.return_value = 200

    # test normal case
    test_object.add_indicator_data_from_rule_key('stochastic', '>30', 'buy', data_mocker)
    # assertions are done in side effect function


@patch('logging.getLogger')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_add_to_data_rule_value(data_mocker, logger_mocker, test_object):
    logger_mocker.return_value = logger_mocker
    logger_mocker.warning.side_effect = logger_side_effect

    data_mocker.add_column.side_effect = add_column_side_effect

    # assemble a price list from the example data
    price_data = []
    for day in EXAMPLE_DATA_MSFT['MSFT']:
        price_data.append(float(day['c']))

    data_mocker.HIGH = DataManager.HIGH
    data_mocker.LOW = DataManager.LOW
    data_mocker.CLOSE = DataManager.CLOSE

    data_mocker.get_column_data.side_effect = get_column_data_side_effect
    data_mocker.get_column_names.return_value = []
    data_mocker.get_data_length.return_value = 200

    # test normal case
    test_object.add_indicator_data_from_rule_value('>stochastic', 'buy', data_mocker)
    # assertions are done in side effect function


def get_column_data_side_effect(*args):
    # stochastic requires high, low, and close data from the data manager
    if args[0] == DataManager.HIGH:
        candle_section = 'h'
    elif args[0] == DataManager.LOW:
        candle_section = 'l'
    else:
        candle_section = 'c'

    price_data = []
    for day in EXAMPLE_DATA_MSFT['MSFT']:
        price_data.append(float(day[candle_section]))
    return price_data


def add_column_side_effect(*args):
    if args[0] == 'stochastic':
        assert args[1] == [67.958,
                           2.785,
                           55.57,
                           19.678,
                           16.355,
                           23.715,
                           44.451,
                           21.612,
                           16.304,
                           18.996,
                           28.901,
                           50.339,
                           19.629,
                           31.343,
                           61.969,
                           71.867,
                           64.366,
                           86.213,
                           91.375,
                           55.975,
                           79.594,
                           54.453,
                           76.437,
                           80.92,
                           99.7,
                           90.065,
                           90.85,
                           81.12,
                           72.781,
                           72.732,
                           46.199,
                           47.769,
                           48.872,
                           49.142,
                           56.106,
                           18.551,
                           29.515,
                           2.64,
                           9.909,
                           11.567,
                           10.976,
                           28.66,
                           73.633,
                           96.652,
                           97.166,
                           65.684,
                           40.0,
                           58.877,
                           55.614,
                           62.07,
                           62.351,
                           52.105,
                           39.825,
                           43.516,
                           28.88,
                           9.669,
                           28.557,
                           28.006,
                           35.721,
                           55.525,
                           73.516,
                           66.301,
                           63.779,
                           65.136,
                           64.706,
                           85.48,
                           35.48,
                           25.71,
                           55.786,
                           63.002,
                           61.51,
                           91.636,
                           87.521,
                           76.74,
                           90.396,
                           89.952,
                           72.094,
                           82.324,
                           93.676,
                           84.007,
                           69.563,
                           73.381,
                           37.282,
                           38.621,
                           1.837,
                           41.667,
                           49.934,
                           36.483,
                           19.619,
                           29.331,
                           7.087,
                           4.199,
                           29.528,
                           88.375,
                           90.251,
                           76.669,
                           96.966,
                           92.82,
                           74.129,
                           87.88,
                           64.619,
                           90.036,
                           89.677,
                           93.497,
                           90.351,
                           91.097,
                           90.575,
                           94.31,
                           85.668,
                           93.548,
                           94.571,
                           84.866,
                           87.348,
                           84.168,
                           62.774,
                           16.023,
                           26.092,
                           33.391,
                           5.205,
                           23.616,
                           49.644,
                           32.822,
                           1.432,
                           12.071,
                           33.471,
                           15.761,
                           47.89,
                           41.48,
                           87.19,
                           77.398,
                           70.758,
                           85.027,
                           81.861,
                           40.899,
                           35.771,
                           74.581,
                           79.035,
                           61.686,
                           37.284,
                           60.942,
                           50.6,
                           24.874,
                           56.155,
                           98.119,
                           95.682,
                           89.859,
                           95.181,
                           96.454,
                           99.381,
                           93.564,
                           97.508,
                           88.323,
                           98.717,
                           99.13,
                           91.705,
                           89.0,
                           96.287,
                           75.996,
                           95.638,
                           94.195,
                           90.974,
                           51.096,
                           38.12,
                           37.024,
                           34.776,
                           12.45,
                           4.303,
                           27.135,
                           41.297,
                           13.946,
                           17.74,
                           3.822,
                           19.148,
                           40.127,
                           38.495,
                           27.454,
                           31.143,
                           51.658,
                           43.869,
                           78.743,
                           84.904,
                           82.748,
                           78.211,
                           78.816,
                           62.609,
                           60.879,
                           49.582,
                           84.937,
                           98.58,
                           80.069,
                           81.63,
                           98.479,
                           96.146,
                           99.587,
                           91.348,
                           82.537,
                           95.52,
                           84.56,
                           95.663,
                           98.85]
    elif args[0] == 'stochastic_30.0':
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
    elif args[0] == 'stochastic_30.0':
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
    assert test_object.check_trigger('stochastic', '>60', data_mocker, None, 0) is False  # noqa

    assert test_object.check_trigger('stochastic', '>60', data_mocker, None, 0) is False  # noqa


@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_value_error(data_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 90

    # ============= Act ==================

    # ============= Assert ===============
    # simple algorithm not hit case
    try:
        assert test_object.check_trigger('12stochastic12', '>60', data_mocker, None, 0)  # noqa
        assert False
    except StrategyIndicatorError:
        assert True


# unless you use @patch.multiple, you must patch full path lengths for multiple methods in the same class
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
    assert test_object.check_trigger('stochastic20', '>price', data_mocker, None, 0) is False  # noqa


def data_side_effect(*args):
    if 'stochastic' not in args[0] and 'Close' not in args[0]:
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
    try:
        test_object.check_trigger('stochasticran50', '>price', data_mocker, None, 0)
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
    assert test_object.check_trigger('stochastic$slope2', '>50', data_mocker, None, 2) is False  # noqa

    # slope used algorithm hit case
    basic_trigger_mocker.return_value = True
    assert test_object.check_trigger('stochastic$slope2', '>50', data_mocker, None, 2) is True  # noqa


def slope_data_side_effect(*args):
    if 'stochastic' not in args[0]:
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
    # simple algorithm not hit case
    try:
        assert test_object.check_trigger('stochastic$slope', '>60', data_mocker, None, 0) is False  # noqa
        assert False
    except StrategyIndicatorError:
        assert True
