import pytest
from unittest.mock import patch
from tests.example_data.ExampleBarsData import EXAMPLE_DATA_MSFT
from StockBench.indicators.ema.trigger import EMATrigger
from StockBench.indicator.exceptions import StrategyIndicatorError


@pytest.fixture
def test_object():
    return EMATrigger('EMA')


def test_additional_days_from_rule_key(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.calculate_additional_days_from_rule_key('EMA20', None) == 20
    assert type(test_object.calculate_additional_days_from_rule_key('EMA20', None)) is int
    assert test_object.calculate_additional_days_from_rule_key('EMA20$slope10', None) == 20
    assert test_object.calculate_additional_days_from_rule_key('EMA20$slope30', None) == 30
    try:
        test_object.calculate_additional_days_from_rule_key('EMA', None)
        assert False
    except StrategyIndicatorError:
        assert True


def test_additional_days_from_rule_value(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.calculate_additional_days_from_rule_value('>EMA20') == 20
    assert type(test_object.calculate_additional_days_from_rule_value('=EMA20')) is int
    assert test_object.calculate_additional_days_from_rule_value('<=EMA20$slope10') == 20
    assert test_object.calculate_additional_days_from_rule_value('>=EMA20$slope30') == 30
    try:
        test_object.calculate_additional_days_from_rule_value('>EMA')
        assert False
    except StrategyIndicatorError:
        assert True


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
    test_object.add_indicator_data_from_rule_key('EMA20', '>120', 'buy', data_mocker)
    # assertions are done in side effect function

    # test console output if no indicator length is provided
    try:
        test_object.add_indicator_data_from_rule_key('EMA', '>120', 'buy', data_mocker)
        assert False
    except StrategyIndicatorError:
        assert True

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
    test_object.add_indicator_data_from_rule_value('>EMA20', '>30', data_mocker)
    # assertions are done in side effect function

    # test console output if no indicator length is provided
    try:
        test_object.add_indicator_data_from_rule_value('<EMA', '>30', data_mocker)
        assert False
    except StrategyIndicatorError:
        assert True

    # ============= Assert ===============
    # assertions are done in side effect function


@patch('StockBench.simulation_data.data_manager.DataManager')
def test_get_value_when_referenced(data_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 234.5

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.get_indicator_value_when_referenced('>=EMA20', data_mocker, 25) == 234.5


def add_column_side_effect(*args):
    assert args[0] == 'EMA20'
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
                       206.741,
                       206.662,
                       206.962,
                       207.311,
                       208.12,
                       209.386,
                       210.666,
                       211.644,
                       212.407,
                       213.097,
                       213.206,
                       213.335,
                       213.473,
                       213.603,
                       213.856,
                       213.503,
                       213.469,
                       212.444,
                       211.677,
                       210.811,
                       210.002,
                       209.632,
                       210.269,
                       211.509,
                       212.662,
                       213.203,
                       212.995,
                       213.319,
                       213.524,
                       213.885,
                       214.219,
                       214.243,
                       213.931,
                       213.777,
                       213.45,
                       213.13,
                       213.2,
                       213.252,
                       213.446,
                       213.522,
                       213.778,
                       213.934,
                       213.966,
                       214.007,
                       214.037,
                       214.223,
                       213.955,
                       213.627,
                       213.593,
                       213.65,
                       213.699,
                       214.222,
                       214.717,
                       215.044,
                       215.761,
                       216.543,
                       216.969,
                       217.516,
                       218.225,
                       218.803,
                       219.077,
                       219.391,
                       219.24,
                       219.123,
                       218.466,
                       218.449,
                       218.554,
                       218.454,
                       218.118,
                       217.955,
                       217.485,
                       217.018,
                       216.963,
                       217.65,
                       218.34,
                       219.054,
                       220.051,
                       221.245,
                       222.373,
                       223.95,
                       224.699,
                       226.117,
                       227.39,
                       228.871,
                       230.112,
                       231.263,
                       232.33,
                       233.422,
                       234.316,
                       235.288,
                       236.219,
                       236.932,
                       237.63,
                       238.217,
                       238.485,
                       238.115,
                       237.654,
                       237.357,
                       236.545,
                       236.13,
                       236.207,
                       235.984,
                       235.181,
                       234.392,
                       234.124,
                       233.486,
                       233.504,
                       233.398,
                       233.766,
                       233.96,
                       234.041,
                       234.389,
                       234.656,
                       234.281,
                       233.865,
                       234.072,
                       234.401,
                       234.502,
                       234.294,
                       234.502,
                       234.575,
                       234.355,
                       234.504,
                       235.255,
                       236.571,
                       237.647,
                       238.813,
                       240.189,
                       241.679,
                       243.039,
                       244.511,
                       245.597,
                       246.927,
                       248.243,
                       249.264,
                       250.123,
                       251.122,
                       251.701,
                       252.599,
                       253.451,
                       254.282,
                       254.323,
                       254.146,
                       253.967,
                       253.768,
                       253.212,
                       252.574,
                       252.301,
                       252.304,
                       251.825,
                       251.292,
                       250.124,
                       249.434,
                       249.312,
                       248.918,
                       248.356,
                       247.859,
                       247.728,
                       247.486,
                       247.806,
                       248.191,
                       248.506,
                       248.62,
                       248.731,
                       248.602,
                       248.481,
                       248.217,
                       248.461,
                       248.976,
                       249.315,
                       249.725,
                       250.441,
                       251.15,
                       251.981,
                       252.604,
                       253.071,
                       253.818,
                       254.342,
                       255.131,
                       256.028]


def logger_side_effect(*args):
    if args[0] == 'Warning: EMA is in incorrect format and will be ignored':
        assert True
    else:
        assert False


# unless you use @patch.multiple, you must patch full path lengths for multiple methods in the same class
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
    assert test_object.check_trigger('EMA20', '>60', data_mocker, None, 0) is False

    # simple algorithm hit case
    basic_trigger_mocker.return_value = True
    assert test_object.check_trigger('EMA20', '>60', data_mocker, None, 0) is True


# unless you use @patch.multiple, you must patch full path lengths for multiple methods in the same class
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_value_error(data_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 90

    # ============= Act ==================

    # ============= Assert ===============
    # simple algorithm not hit case
    try:
        test_object.check_trigger('EMA', '>60', data_mocker, None, 0)
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
    assert test_object.check_trigger('EMA20', '>$price', data_mocker, None, 0) is False


def data_side_effect(*args):
    if 'EMA' not in args[0] and 'Close' not in args[0]:
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
        assert test_object.check_trigger('EMA20ran50', '>$price', None, None, 0)  # noqa
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
    assert test_object.check_trigger('EMA20$slope2', '>50', data_mocker, None, 2) is False

    # slope used algorithm hit case
    basic_trigger_mocker.return_value = True
    assert test_object.check_trigger('EMA20$slope2', '>50', data_mocker, None, 2) is True


def slope_data_side_effect(*args):
    if 'EMA' not in args[0]:
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
        test_object.check_trigger('EMA20$slope', '>60', data_mocker, None, 0)
        assert False
    except StrategyIndicatorError:
        assert True
