import pytest
from unittest.mock import patch

from StockBench.controllers.simulator.indicator.exceptions import StrategyIndicatorError
from StockBench.controllers.simulator.indicators.candlestick_color.trigger import CandlestickColorTrigger


@pytest.fixture
def test_object():
    return CandlestickColorTrigger('color')


def test_additional_days_from_rule_key_normal(test_object):
    # ============= Arrange ==============

    # ============= Act ==================
    actual = test_object.calculate_additional_days_from_rule_key('color', {'0': 'green', '1': 'red'})

    # ============= Assert ===============
    assert type(actual) is int
    assert actual == 1


def test_additional_days_from_rule_key_no_values(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    try:
        test_object.calculate_additional_days_from_rule_key('color', {})
        assert False
    except StrategyIndicatorError:
        assert True


def test_additional_days_from_rule_value(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.calculate_additional_days_from_rule_value({'0': 'green', '1': 'red'}) == 0


def test_add_to_data_from_rule_key(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    try:
        test_object.add_indicator_data_from_rule_key('', '', '', None)  # noqa
        assert True
    except Exception as e:
        print(e)
        assert False


def test_add_to_data_from_rule_value(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    try:
        test_object.add_indicator_data_from_rule_value('', '', None)  # noqa
        assert True
    except Exception as e:
        print(e)
        assert False


def test_get_value_when_referenced(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    try:
        test_object.get_indicator_value_when_referenced({'0': 'green', '1': 'red'}, None, 1)  # noqa
        assert False
    except NotImplementedError:
        assert True


@patch('StockBench.controllers.simulator.simulation_data.data_manager.DataManager')
def test_check_trigger(data_mocker, test_object):
    # ============= Arrange ==============
    current_day_index = 0

    data_mocker.COLOR = "color"
    data_mocker.get_data_point.side_effect = mock_colors_even

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.check_trigger('color', {'0': 'green', '1': 'red'}, data_mocker, None,  # noqa
                                     current_day_index) is True

    assert test_object.check_trigger('color', {'0': 'red', '1': 'green'}, data_mocker, None,  # noqa
                                     current_day_index) is False


@patch('StockBench.controllers.simulator.simulation_data.data_manager.DataManager')
def test_check_trigger_no_values(data_mocker, test_object):
    # ============= Arrange ==============
    current_day_index = 0

    data_mocker.COLOR = "color"
    data_mocker.get_data_point.side_effect = mock_colors_even

    # ============= Act ==================

    # ============= Assert ===============
    try:
        test_object.check_trigger('color', {}, data_mocker, None, current_day_index)  # noqa
        assert False
    except StrategyIndicatorError:
        assert True


def mock_colors_even(*args):
    if args[1] % 2 == 0:
        return 'green'
    else:
        return 'red'
