import pytest
from tests.example_data.ExampleBarsData import EXAMPLE_DATA_MSFT
from StockBench.controllers.simulator.simulation_data.data_manager import DataManager
from StockBench.controllers.simulator.indicators.stochastic.trigger import StochasticTrigger
from StockBench.controllers.simulator.indicator.exceptions import StrategyIndicatorError

# NOTE: mocker is a fixture provided by pytest plugin pip package "pytest-mock"
# (pytest version of @patch)


@pytest.fixture
def logger_mocker(mocker):
    return mocker.patch('logging.Logger')


@pytest.fixture
def data_mocker(mocker):
    return mocker.patch('StockBench.controllers.simulator.simulation_data.data_manager.DataManager')


@pytest.fixture
def trigger_interface_mocker(mocker):
    # WARNING: for static functions, you must mock the path it is used at (stochastic.trigger)
    return mocker.patch('StockBench.controllers.simulator.indicators.stochastic.trigger.TriggerInterface')


@pytest.fixture
def test_object():
    return StochasticTrigger('stochastic')


def test_additional_days_from_rule_key():
    test_object = StochasticTrigger('stochastic')
    assert test_object.calculate_additional_days_from_rule_key('stochastic', None) == 14
    assert test_object.calculate_additional_days_from_rule_key('stochastic20', None) == 20
    assert test_object.calculate_additional_days_from_rule_key('stochastic20$slope10', None) == 20
    assert test_object.calculate_additional_days_from_rule_key('stochastic20$slope30', None) == 30


def test_additional_days_from_rule_value():
    test_object = StochasticTrigger('stochastic')
    assert test_object.calculate_additional_days_from_rule_value('stochastic') == 14
    assert test_object.calculate_additional_days_from_rule_value('stochastic20') == 20
    assert test_object.calculate_additional_days_from_rule_value('stochastic20$slope10') == 20
    assert test_object.calculate_additional_days_from_rule_value('stochastic20$slope30') == 30


def test_add_to_data_rule_key(data_mocker, logger_mocker, test_object):
    setup_logger_mocker(logger_mocker)

    setup_data_mocker(data_mocker)

    test_object.add_indicator_data_from_rule_key('stochastic', '>30', 'buy', data_mocker)
    # assertions are done in side effect function


def test_add_to_data_rule_key_non_default_length(data_mocker, logger_mocker, test_object):
    setup_logger_mocker(logger_mocker)

    setup_data_mocker(data_mocker)

    test_object.add_indicator_data_from_rule_key('stochastic30', '>30', 'buy', data_mocker)
    # assertions are done in side effect function


def test_add_to_data_rule_value(data_mocker, logger_mocker, test_object):
    setup_logger_mocker(logger_mocker)

    setup_data_mocker(data_mocker)

    test_object.add_indicator_data_from_rule_value('>stochastic', 'buy', data_mocker)
    # assertions are done in side effect function


def test_add_to_data_rule_value_non_default_length(data_mocker, logger_mocker, test_object):
    setup_logger_mocker(logger_mocker)

    setup_data_mocker(data_mocker)

    test_object.add_indicator_data_from_rule_value('>stochastic30', 'buy', data_mocker)
    # assertions are done in side effect function


def test_indicator_already_in_data_manager(data_mocker, logger_mocker, test_object):
    setup_logger_mocker(logger_mocker)

    data_mocker.get_column_names.return_value = ['stochastic']

    # should not try to add column to data manager
    data_mocker.add_column.side_effect = fail_if_called_side_effect

    # test both rule key and rule value to be sure it works for both
    # (from rule key without numeric limits in rule key to avoid the add_column call in the value based block)

    test_object.add_indicator_data_from_rule_key('stochastic', '>RSI', 'buy', data_mocker)
    test_object.add_indicator_data_from_rule_value('>stochastic', 'buy', data_mocker)

    # test passed if side effect was not called (did not fail)
    assert True


def test_get_value_when_referenced(data_mocker, test_object):
    data_mocker.get_data_point.return_value = 234.5

    assert test_object.get_indicator_value_when_referenced('>=stochastic', data_mocker, 25) == 234.5


def test_check_trigger(data_mocker, trigger_interface_mocker, logger_mocker, test_object):
    data_mocker.get_data_point.return_value = 10

    trigger_interface_mocker.parse_rule_key.return_value = 25.5

    assert test_object.check_trigger('stochastic', '>60', data_mocker, None, 0) is False


def test_check_trigger_value_error(data_mocker, test_object):
    data_mocker.get_data_point.return_value = 90

    try:
        assert test_object.check_trigger('12stochastic12', '>60', data_mocker, None, 0)
        assert False
    except StrategyIndicatorError:
        assert True


# def test_check_trigger_current_price_symbol_used(data_mocker, trigger_interface_mocker, logger_mocker, test_object):
#     setup_logger_mocker(logger_mocker)
#
#     data_mocker.get_data_point.side_effect = data_point_side_effect
#     data_mocker.CLOSE = 'Close'
#
#     trigger_interface_mocker.parse_rule_key.return_value = 25.5
#
#     assert test_object.check_trigger('stochastic20', '>$price', data_mocker, None, 0) is False


def data_point_side_effect(*args):
    if 'stochastic' not in args[0] and 'Close' not in args[0]:
        assert False
    if args[0] == 'close':
        return 100.1
    else:
        return 40.2


def test_check_trigger_2_numbers_present_bad_format(data_mocker, test_object):
    data_mocker.get_data_point.side_effect = data_point_side_effect
    data_mocker.CLOSE = 'Close'

    try:
        test_object.check_trigger('stochasticran50', '>price', data_mocker, None, 0)
        assert False
    except StrategyIndicatorError:
        assert True


def test_check_trigger_slope_used(data_mocker, trigger_interface_mocker, logger_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.side_effect = slope_data_side_effect

    trigger_interface_mocker.parse_rule_key.return_value = 25.5

    # ============= Act ==================

    # ============= Assert ===============
    # slope used algorithm not hit case
    assert test_object.check_trigger('stochastic$slope2', '>50', data_mocker, None, 2) is False
    assert test_object.check_trigger('stochastic$slope2', '>20', data_mocker, None, 2) is True


def test_check_trigger_slope_value_error(data_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 90

    # ============= Act ==================

    # ============= Assert ===============
    # simple algorithm not hit case
    try:
        assert test_object.check_trigger('stochastic$slope', '>60', data_mocker, None, 0) is False
        assert False
    except StrategyIndicatorError:
        assert True


def setup_logger_mocker(logger_mocker):
    logger_mocker.return_value = logger_mocker
    logger_mocker.warning.side_effect = logger_side_effect


def setup_data_mocker(data_mocker):
    data_mocker.add_column.side_effect = add_column_side_effect

    data_mocker.HIGH = DataManager.HIGH
    data_mocker.LOW = DataManager.LOW
    data_mocker.CLOSE = DataManager.CLOSE

    data_mocker.get_column_data.side_effect = get_column_data_side_effect
    data_mocker.get_column_names.return_value = []
    data_mocker.get_data_length.return_value = 200


def get_column_data_side_effect(*args):
    # stochastic requires high, low, and close data from the data manager
    if args[0] == DataManager.HIGH:
        candle_section = 'h'
    elif args[0] == DataManager.LOW:
        candle_section = 'l'
    else:
        candle_section = 'c'

    return [float(day[candle_section]) for day in EXAMPLE_DATA_MSFT['MSFT']]


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
    elif args[0] == '30stochastic':
        assert args[1] == [67.958, 2.785, 55.57, 19.678, 16.355, 23.715, 44.451, 21.612, 16.304, 18.996, 28.901, 50.339,
                           19.629, 31.343, 52.103, 60.425, 49.344, 63.637, 73.316, 44.912, 63.863, 43.691, 61.33,
                           65.039, 88.467, 91.126, 91.782, 85.221, 80.836, 80.801, 62.12, 63.225, 64.002, 64.192,
                           69.095, 47.997, 58.356, 22.307, 28.108, 21.505, 11.995, 26.605, 65.821, 92.497, 93.787,
                           65.684, 40.0, 58.877, 55.614, 62.07, 62.351, 52.105, 39.825, 44.526, 37.614, 36.737, 49.965,
                           49.579, 54.982, 51.298, 58.211, 55.439, 51.404, 51.86, 51.579, 57.439, 41.368, 38.228,
                           47.895, 50.232, 44.16, 55.261, 56.413, 50.05, 72.194, 90.498, 73.612, 83.286, 94.012,
                           84.805, 71.083, 74.711, 50.736, 51.788, 21.346, 51.474, 57.775, 46.431, 32.208, 40.398,
                           21.638, 19.203, 40.564, 83.398, 87.382, 79.819, 97.376, 93.63, 74.211, 87.915, 64.723,
                           90.065, 89.707, 93.514, 90.377, 91.282, 92.097, 96.109, 90.848, 95.88, 97.469, 92.922,
                           94.531, 93.156, 85.044, 66.188, 62.287, 66.012, 49.267, 59.12, 73.05, 63.403, 35.574,
                           18.895, 33.592, 14.605, 43.073, 37.174, 59.442, 52.766, 48.24, 61.408, 59.122, 29.538,
                           25.834, 53.864, 60.677, 51.212, 36.854, 55.876, 50.343, 39.9, 59.278, 92.5, 96.537,
                           91.868, 96.1, 97.058, 99.496, 94.882, 97.996, 90.61, 98.963, 99.247, 92.664, 90.041,
                           97.292, 85.877, 97.996, 97.325, 97.015, 74.941, 68.292, 67.731, 65.779, 52.446, 48.021,
                           57.993, 66.158, 50.39, 47.142, 21.558, 19.212, 40.127, 28.304, 19.705, 20.183, 33.479,
                           28.344, 50.876, 54.857, 53.463, 46.298, 46.656, 37.062, 36.863, 30.414, 50.597, 62.898,
                           57.604, 84.191, 98.865, 97.077, 99.68, 93.294, 86.362, 96.453, 87.701, 96.503, 99.062]
    else:
        assert False


def fail_if_called_side_effect(*args):  # noqa
    assert False


def logger_side_effect(*args):
    if args[0] == 'Warning: stochastic is in incorrect format and will be ignored':
        assert True
    else:
        assert False


def slope_data_side_effect(*args):
    if 'stochastic' not in args[0]:
        assert False
    if args[1] % 2 == 0:
        return 200.0
    else:
        return 100.0
