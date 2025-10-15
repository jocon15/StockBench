import pytest
from unittest.mock import patch
from StockBench.controllers.simulator.indicators import StopProfitTrigger


@pytest.fixture
def test_object():
    return StopProfitTrigger('stop_profit')


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


@patch('StockBench.position.position.Position')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_intraday_percent_hit_case(data_mocker, position_mocker, test_object):
    # ============= Arrange ==============
    position_mocker.intraday_profit_loss.return_value = 150
    position_mocker.intraday_profit_loss_percent.return_value = 1.5

    # ============= Act ==================
    actual = test_object.check_trigger('stop_profit_intraday', '1%', data_mocker, position_mocker, 0)

    # ============= Assert ===============
    assert position_mocker.intraday_profit_loss_percent.called is True
    assert actual is True


@patch('StockBench.position.position.Position')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_intraday_percent_not_hit_case(data_mocker, position_mocker, test_object):
    # ============= Arrange ==============
    position_mocker.intraday_profit_loss.return_value = -50
    position_mocker.intraday_profit_loss_percent.return_value = -0.5

    # ============= Act ==================
    actual = test_object.check_trigger('stop_profit_intraday', '1%', data_mocker, position_mocker, 0)

    # ============= Assert ===============
    assert position_mocker.profit_loss_percent.called is True
    assert actual is False


@patch('StockBench.position.position.Position')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_intraday_hit_case(data_mocker, position_mocker, test_object):
    # ============= Arrange ==============
    position_mocker.intraday_profit_loss.return_value = 1500

    # ============= Act ==================
    actual = test_object.check_trigger('stop_profit_intraday', '1000', data_mocker, position_mocker, 0)

    # ============= Assert ===============
    assert position_mocker.profit_loss_percent.called is True
    assert actual is True


@patch('StockBench.position.position.Position')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_intraday_not_hit_case(data_mocker, position_mocker, test_object):
    # ============= Arrange ==============
    position_mocker.intraday_profit_loss.return_value = -150

    # ============= Act ==================
    actual = test_object.check_trigger('stop_profit_intraday', '1000', data_mocker, position_mocker, 0)

    # ============= Assert ===============
    assert position_mocker.profit_loss_percent.called is True
    assert actual is False


@patch('StockBench.position.position.Position')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_lifetime_percent_hit_case(data_mocker, position_mocker, test_object):
    # ============= Arrange ==============
    position_mocker.profit_loss.return_value = 110
    position_mocker.profit_loss_percent.return_value = 1.1

    # ============= Act ==================
    actual = test_object.check_trigger('stop_profit', '1%', data_mocker, position_mocker, 0)

    # ============= Assert ===============
    assert position_mocker.profit_loss_percent.called is True
    assert actual is True


@patch('StockBench.position.position.Position')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_lifetime_percent_not_hit_case(data_mocker, position_mocker, test_object):
    # ============= Arrange ==============
    position_mocker.profit_loss.return_value = -10
    position_mocker.profit_loss_percent.return_value = -0.1

    # ============= Act ==================
    actual = test_object.check_trigger('stop_profit', '1%', data_mocker, position_mocker, 0)

    # ============= Assert ===============
    assert position_mocker.profit_loss_percent.called is True
    assert actual is False


@patch('StockBench.position.position.Position')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_lifetime_hit_case(data_mocker, position_mocker, test_object):
    # ============= Arrange ==============
    position_mocker.profit_loss.return_value = 1500

    # ============= Act ==================
    actual = test_object.check_trigger('stop_profit', '1000', data_mocker, position_mocker, 0)

    # ============= Assert ===============
    assert position_mocker.profit_loss_percent.called is True
    assert actual is True


@patch('StockBench.position.position.Position')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_lifetime_not_hit_case(data_mocker, position_mocker, test_object):
    # ============= Arrange ==============
    position_mocker.profit_loss.return_value = -100

    # ============= Act ==================
    actual = test_object.check_trigger('stop_profit', '1000', data_mocker, position_mocker, 0)

    # ============= Assert ===============
    assert position_mocker.profit_loss_percent.called is True
    assert actual is False


@patch('StockBench.position.position.Position')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_lifetime_not_hit_case_positive(data_mocker, position_mocker, test_object):
    # ============= Arrange ==============
    position_mocker.profit_loss.return_value = 100

    # ============= Act ==================
    actual = test_object.check_trigger('stop_profit', '1000', data_mocker, position_mocker, 0)

    # ============= Assert ===============
    assert position_mocker.profit_loss_percent.called is True
    assert actual is False
