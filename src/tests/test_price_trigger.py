import pytest
from unittest.mock import patch
from StockBench.controllers.simulator.indicators.price.price import PriceTrigger
from StockBench.controllers.simulator.indicator import StrategyIndicatorError


@pytest.fixture
def test_object():
    return PriceTrigger('price')


def test_additional_days_from_rule_key(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.calculate_additional_days_from_rule_key('>123.2', None) == 0


def test_additional_days_from_rule_value(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.calculate_additional_days_from_rule_value('>123.2') == 0


def test_add_to_data_from_rule_key(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    try:
        test_object.add_indicator_data_from_rule_key('', None, '', '')
        assert True
    except Exception as e:
        print(f'Unexpected exception {e}')
        assert False


def test_add_to_data_from_rule_value(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    try:
        test_object.add_indicator_data_from_rule_value('', '', None)  # noqa
        assert True
    except Exception as e:
        print(f'Unexpected exception {e}')
        assert False


@patch('StockBench.simulation_data.data_manager.DataManager')
def test_get_value_when_referenced(data_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 234.5

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.get_indicator_value_when_referenced('>=price', data_mocker, 25) == 234.5


@patch('StockBench.algorithm.algorithm.Trigger.find_single_numeric_in_str')
@patch('StockBench.algorithm.algorithm.Trigger.find_operator_in_str')
@patch('StockBench.algorithm.algorithm.Trigger.basic_trigger_check')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger(data_mocker, basic_trigger_mocker, operator_mocker, numeric_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.side_effect = None
    basic_trigger_mocker.return_value = False
    operator_mocker.return_value = None
    numeric_mocker.return_value = None

    # ============= Act ==================

    # ============= Assert ===============
    # algorithm not hit
    assert (test_object.check_trigger('price', '>350', data_mocker, None, 2)
            is False)

    # algorithm hit
    basic_trigger_mocker.return_value = True
    assert (test_object.check_trigger('price', '>350', data_mocker, None, 2)
            is True)


@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_value_error(data_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 90

    # ============= Act ==================

    # ============= Assert ===============
    try:
        test_object.check_trigger('price$slope', '>60', data_mocker, None, 0)
        assert False
    except StrategyIndicatorError:
        assert True
