import pytest
from unittest.mock import patch
from tests.example_data.ExampleBarsData import EXAMPLE_DATA_MSFT
from StockBench.indicators.sma.trigger import SMATrigger
from StockBench.indicator.exceptions import StrategyIndicatorError


@pytest.fixture
def test_object():
    return SMATrigger('SMA')


def test_additional_days_from_rule_key(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.calculate_additional_days_from_rule_key('SMA20', None) == 20
    assert type(test_object.calculate_additional_days_from_rule_key('SMA20', None)) is int
    assert test_object.calculate_additional_days_from_rule_key('SMA20$slope10', None) == 20
    assert test_object.calculate_additional_days_from_rule_key('SMA20$slope30', None) == 30
    try:
        test_object.calculate_additional_days_from_rule_key('SMA', None)
        assert False
    except StrategyIndicatorError:
        assert True


def test_additional_days_from_rule_value(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.calculate_additional_days_from_rule_value('SMA20') == 20
    assert type(test_object.calculate_additional_days_from_rule_value('SMA20')) is int
    assert test_object.calculate_additional_days_from_rule_value('SMA20$slope10') == 20
    assert test_object.calculate_additional_days_from_rule_value('SMA20$slope30') == 30
    try:
        test_object.calculate_additional_days_from_rule_value('SMA')
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
    test_object.add_indicator_data_from_rule_key('SMA20', '>30', 'buy', data_mocker)
    # assertions are done in side effect function

    # test console output if no indicator length is provided
    try:
        test_object.add_indicator_data_from_rule_key('SMA', '>30', 'buy', data_mocker)
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
    test_object.add_indicator_data_from_rule_value('>SMA20', 'buy', data_mocker)
    # assertions are done in side effect function

    # test console output if no indicator length is provided
    try:
        test_object.add_indicator_data_from_rule_value('<SMA', 'sell', data_mocker)
        assert False
    except StrategyIndicatorError:
        assert True

    # ============= Assert ===============
    # assertions are done in side effect function


def add_column_side_effect(*args):
    assert args[0] == 'SMA20'
    assert args[1] == [214.14,
                       208.395,
                       209.323,
                       208.338,
                       207.478,
                       207.115,
                       207.363,
                       207.06,
                       206.604,
                       205.989,
                       205.685,
                       205.826,
                       205.423,
                       205.263,
                       205.43,
                       205.691,
                       205.778,
                       206.03,
                       206.368,
                       206.359,
                       206.171,
                       206.334,
                       206.265,
                       206.528,
                       207.116,
                       207.922,
                       208.62,
                       209.42,
                       210.255,
                       211.215,
                       211.795,
                       212.154,
                       212.864,
                       213.447,
                       213.871,
                       213.898,
                       214.198,
                       213.817,
                       213.414,
                       213.234,
                       212.831,
                       212.842,
                       213.167,
                       213.8,
                       214.191,
                       214.037,
                       213.447,
                       213.22,
                       213.011,
                       212.894,
                       213.051,
                       213.047,
                       212.856,
                       212.73,
                       212.434,
                       212.43,
                       212.466,
                       213.018,
                       213.563,
                       214.146,
                       214.84,
                       215.305,
                       215.203,
                       214.758,
                       214.293,
                       214.176,
                       214.196,
                       213.901,
                       213.791,
                       213.635,
                       213.474,
                       213.71,
                       214.132,
                       214.424,
                       215.036,
                       215.73,
                       216.088,
                       216.536,
                       217.019,
                       217.522,
                       217.795,
                       218.143,
                       218.32,
                       218.5,
                       218.395,
                       218.51,
                       218.917,
                       219.267,
                       219.35,
                       219.46,
                       219.404,
                       219.073,
                       218.924,
                       219.226,
                       219.342,
                       219.435,
                       219.861,
                       220.354,
                       220.761,
                       221.493,
                       221.999,
                       222.86,
                       223.944,
                       225.19,
                       226.674,
                       227.87,
                       229.016,
                       230.331,
                       231.725,
                       233.13,
                       234.732,
                       236.289,
                       237.68,
                       238.66,
                       239.467,
                       239.905,
                       240.092,
                       240.19,
                       239.977,
                       239.64,
                       239.897,
                       239.611,
                       239.014,
                       238.212,
                       237.696,
                       236.957,
                       236.518,
                       235.947,
                       235.669,
                       235.233,
                       234.721,
                       234.42,
                       234.066,
                       233.413,
                       232.857,
                       232.929,
                       233.142,
                       233.188,
                       233.363,
                       233.577,
                       233.494,
                       233.413,
                       233.832,
                       234.606,
                       235.481,
                       236.503,
                       237.314,
                       238.357,
                       239.285,
                       240.293,
                       241.477,
                       242.388,
                       243.507,
                       245.008,
                       246.46,
                       247.572,
                       248.726,
                       249.814,
                       251.254,
                       252.507,
                       253.853,
                       254.976,
                       255.803,
                       256.296,
                       256.437,
                       256.44,
                       256.271,
                       256.094,
                       255.919,
                       255.484,
                       254.871,
                       254.027,
                       253.193,
                       252.563,
                       251.874,
                       251.111,
                       250.238,
                       249.702,
                       248.905,
                       248.37,
                       247.853,
                       247.693,
                       247.555,
                       247.431,
                       247.206,
                       247.176,
                       247.136,
                       247.189,
                       247.266,
                       247.53,
                       247.899,
                       248.81,
                       249.56,
                       250.147,
                       250.814,
                       251.538,
                       252.427,
                       253.069,
                       253.941,
                       254.626]


def logger_side_effect(*args):
    if args[0] == 'Warning: SMA is in incorrect format and will be ignored':
        assert True
    else:
        assert False


@patch('StockBench.simulation_data.data_manager.DataManager')
def test_get_value_when_referenced(data_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 234.5

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.get_indicator_value_when_referenced('>=SMA20', data_mocker, 25) == 234.5


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
    assert test_object.check_trigger('SMA20', '>60', data_mocker, None, 0) is False  # noqa

    # simple algorithm hit case
    basic_trigger_mocker.return_value = True
    assert test_object.check_trigger('SMA20', '>60', data_mocker, None, 0) is True  # noqa


# unless you use @patch.multiple, you must patch full path lengths for multiple methods in the same class
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_value_error(data_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 90

    # ============= Act ==================

    # ============= Assert ===============
    # simple algorithm not hit case
    try:
        test_object.check_trigger('SMA', '>', data_mocker, None, 0)  # noqa
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
    assert test_object.check_trigger('SMA20', '>price', data_mocker, None, 0) is False  # noqa


def data_side_effect(*args):
    if 'SMA' not in args[0] and 'Close' not in args[0]:
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
        test_object.check_trigger('SMA20ran50', '>price', data_mocker, None, 0)  # noqa
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
    assert test_object.check_trigger('SMA20$slope2', '>50', data_mocker, None, 2) is False  # noqa

    # slope used algorithm hit case
    basic_trigger_mocker.return_value = True
    assert test_object.check_trigger('SMA20$slope2', '>50', data_mocker, None, 2) is True  # noqa


def slope_data_side_effect(*args):
    if 'SMA' not in args[0]:
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
        test_object.check_trigger('SMA20$slope', '>60', data_mocker, None, 0)  # noqa
        assert False
    except StrategyIndicatorError:
        assert True
