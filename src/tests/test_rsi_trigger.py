import pytest
from unittest.mock import patch
from tests.example_data.ExampleBarsData import EXAMPLE_DATA_MSFT
from StockBench.indicators.rsi.trigger import RSITrigger
from StockBench.indicator.exceptions import StrategyIndicatorError


@pytest.fixture
def test_object():
    return RSITrigger('RSI')


def test_additional_days_from_rule_key(test_object):
    assert test_object.additional_days_from_rule_key('RSI', None) == 14
    assert test_object.additional_days_from_rule_key('RSI50', None) == 50
    assert test_object.additional_days_from_rule_key('RSI20$slope10', None) == 20
    assert test_object.additional_days_from_rule_key('RSI20$slope30', None) == 30


def test_additional_days_from_rule_value(test_object):
    assert test_object.additional_days_from_rule_value('RSI') == 14
    assert test_object.additional_days_from_rule_value('RSI50') == 50
    assert test_object.additional_days_from_rule_value('RSI20$slope10') == 20
    assert test_object.additional_days_from_rule_value('RSI20$slope30') == 30


@patch('logging.getLogger')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_add_to_data_from_rule_key(data_mocker, logger_mocker, test_object):
    logger_mocker.return_value = logger_mocker
    logger_mocker.warning.side_effect = logger_side_effect

    data_mocker.add_column.side_effect = add_column_side_effect

    # assemble a price list from the example data
    price_data = []
    for day in EXAMPLE_DATA_MSFT['MSFT']:
        price_data.append(float(day['c']))

    data_mocker.get_column_data.return_value = price_data
    data_mocker.get_column_names.return_value = []
    data_mocker.get_data_length.return_value = 200

    # test normal case
    test_object.add_to_data_from_rule_key('RSI', '>30', 'buy', data_mocker)
    # assertions are done in side effect function


@patch('logging.getLogger')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_add_to_data_from_rule_value(data_mocker, logger_mocker, test_object):
    logger_mocker.return_value = logger_mocker
    logger_mocker.warning.side_effect = logger_side_effect

    data_mocker.add_column.side_effect = add_column_side_effect

    # assemble a price list from the example data
    price_data = []
    for day in EXAMPLE_DATA_MSFT['MSFT']:
        price_data.append(float(day['c']))

    data_mocker.get_column_data.return_value = price_data
    data_mocker.get_column_names.return_value = []
    data_mocker.get_data_length.return_value = 200

    # test normal case
    test_object.add_to_data_from_rule_value('RSI', '>30', data_mocker)
    # assertions are done in side effect function


def add_column_side_effect(*args):
    if args[0] == 'RSI':
        assert args[1] == [0,
                           0,
                           42.607,
                           49.665,
                           57.87,
                           44.079,
                           41.727,
                           44.106,
                           47.555,
                           49.674,
                           46.289,
                           47.365,
                           45.625,
                           44.09,
                           44.802,
                           43.111,
                           44.677,
                           44.298,
                           43.277,
                           42.251,
                           42.716,
                           42.855,
                           43.071,
                           41.582,
                           42.518,
                           41.008,
                           41.092,
                           42.447,
                           43.953,
                           45.928,
                           45.227,
                           43.427,
                           42.273,
                           39.321,
                           38.536,
                           40.973,
                           39.849,
                           37.751,
                           37.638,
                           37.438,
                           39.049,
                           39.506,
                           44.721,
                           46.318,
                           44.25,
                           42.729,
                           40.69,
                           43.257,
                           45.804,
                           43.922,
                           40.507,
                           40.299,
                           41.567,
                           41.514,
                           42.719,
                           43.557,
                           45.781,
                           46.395,
                           47.199,
                           46.646,
                           47.772,
                           50.337,
                           53.416,
                           52.663,
                           60.518,
                           59.748,
                           57.413,
                           56.903,
                           57.541,
                           55.787,
                           60.33,
                           56.872,
                           51.341,
                           58.02,
                           61.413,
                           58.119,
                           55.705,
                           55.568,
                           57.471,
                           60.143,
                           61.269,
                           60.732,
                           57.552,
                           54.249,
                           48.406,
                           52.582,
                           51.973,
                           50.21,
                           48.91,
                           50.058,
                           47.981,
                           48.531,
                           50.288,
                           53.873,
                           53.74,
                           50.821,
                           53.306,
                           52.359,
                           51.715,
                           54.57,
                           49.595,
                           52.964,
                           55.988,
                           57.492,
                           57.389,
                           57.442,
                           54.172,
                           54.215,
                           53.535,
                           53.674,
                           51.58,
                           51.523,
                           46.269,
                           48.066,
                           46.542,
                           43.994,
                           46.13,
                           46.571,
                           46.627,
                           48.487,
                           49.269,
                           48.567,
                           46.147,
                           47.89,
                           49.027,
                           46.684,
                           50.353,
                           54.127,
                           53.548,
                           52.623,
                           52.657,
                           49.488,
                           49.821,
                           46.544,
                           46.342,
                           48.114,
                           48.866,
                           49.281,
                           51.358,
                           53.667,
                           53.746,
                           55.579,
                           56.85,
                           59.232,
                           61.942,
                           63.222,
                           63.81,
                           64.618,
                           64.319,
                           62.459,
                           61.526,
                           64.306,
                           63.144,
                           61.365,
                           60.472,
                           63.311,
                           63.037,
                           61.271,
                           60.112,
                           59.522,
                           57.448,
                           52.837,
                           51.963,
                           52.176,
                           56.723,
                           54.28,
                           54.768,
                           54.478,
                           51.899,
                           50.472,
                           50.594,
                           47.726,
                           45.644,
                           48.022,
                           46.904,
                           47.165,
                           44.793,
                           45.374,
                           45.68,
                           49.521,
                           48.513,
                           48.723,
                           49.773,
                           47.26,
                           50.877,
                           52.628,
                           51.477,
                           54.203,
                           54.7,
                           53.975,
                           52.049,
                           54.201,
                           54.214,
                           53.424,
                           55.473,
                           55.812,
                           56.32,
                           59.354,
                           59.01,
                           56.741]
    elif args[0] == 'RSI_30.0':
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
    elif args[0] == 'RSI_60.0':
        assert args[1] == [60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0,
                           60.0]
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
    assert test_object.get_value_when_referenced('>=MACD', data_mocker, 25) == 234.5


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
    assert test_object.check_trigger('RSI', '>60', data_mocker, None, 0) is False  # noqa

    assert test_object.check_trigger('RSI', '>60', data_mocker, None, 0) is False  # noqa


@patch('StockBench.algorithm.algorithm.Trigger.find_single_numeric_in_str')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_value_error(data_mocker, numeric_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 90

    # ============= Act ==================

    # ============= Assert ===============
    # simple algorithm not hit case
    try:
        assert test_object.check_trigger('12RSI12', '>60', data_mocker, None, 0)  # noqa
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
    assert test_object.check_trigger('RSI20', '>$price', data_mocker, None, 0) is False  # noqa


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
    try:
        test_object.check_trigger('RSIran50', '>$price', data_mocker, None, 0)  # noqa
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
    assert test_object.check_trigger('RSI$slope2', '>50', data_mocker, None, 2) is False  # noqa

    # slope used algorithm hit case
    basic_trigger_mocker.return_value = True
    assert test_object.check_trigger('RSI$slope2', '>50', data_mocker, None, 2) is True  # noqa


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
    # simple algorithm not hit case
    try:
        assert test_object.check_trigger('RSI$slope', '>60', data_mocker, None, 0) is False  # noqa
        assert False
    except StrategyIndicatorError:
        assert True
