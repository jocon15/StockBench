import pytest
from unittest.mock import patch
from StockBench.controllers.simulator.indicators.volume.trigger import VolumeTrigger


@pytest.fixture
def test_object():
    return VolumeTrigger('volume')


def test_additional_days_from_rule_key(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.calculate_additional_days_from_rule_key('', None) == 0


def test_additional_days_from_rule_value(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.calculate_additional_days_from_rule_value('') == 0


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
        test_object.get_indicator_value_when_referenced('', None, 25)  # noqa
        assert False
    except NotImplementedError:
        assert True


@patch('StockBench.controllers.simulator.algorithm.algorithm.Trigger.find_single_numeric_in_str')
@patch('StockBench.controllers.simulator.algorithm.algorithm.Trigger.find_operator_in_str')
@patch('StockBench.controllers.simulator.algorithm.algorithm.Trigger.basic_trigger_check')
@patch('StockBench.controllers.simulator.simulation_data.data_manager.DataManager')
def test_check_trigger(data_mocker, basic_trigger_mocker, operator_mocker, numeric_mocker, test_object):
    # ============= Arrange ==============
    data_mocker.get_data_point.side_effect = None
    basic_trigger_mocker.return_value = False
    operator_mocker.return_value = None
    numeric_mocker.return_value = None

    # ============= Act ==================

    # ============= Assert ===============
    # algorithm not hit
    assert (test_object.check_trigger('volume', '>350', data_mocker, None, 2)  # noqa
            is False)

    # algorithm hit
    basic_trigger_mocker.return_value = True
    assert (test_object.check_trigger('volume', '>350', data_mocker, None, 2)  # noqa
            is True)
