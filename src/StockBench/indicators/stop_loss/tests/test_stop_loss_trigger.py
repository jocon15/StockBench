import os
import sys
import pytest
from unittest.mock import patch

# allows import out a directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


from StockBench.indicators.stop_loss.trigger import StopLossTrigger


@pytest.fixture
def test_object():
    return StopLossTrigger('stop_loss')


def test_additional_days(test_object):
    # ============= Arrange ==============

    # ============= Act ==================
    actual = test_object.additional_days('', '')

    # ============= Assert ===============
    assert type(actual) is int
    assert actual == 0


def test_add_to_data(test_object):
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    try:
        test_object.add_to_data('', '', '', None)
        assert True
    except Exception as e:
        print(e)
        assert False


@patch('StockBench.position.position.Position')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_intraday_percent_hit_case(data_mocker, position_mocker, test_object):
    # ============= Arrange ==============
    position_mocker.intraday_profit_loss_percent.return_value = -1.5

    # ============= Act ==================
    actual = test_object.check_trigger('stop_loss_intraday', '1%', data_mocker, position_mocker, 0)

    # ============= Assert ===============
    assert position_mocker.profit_loss_percent.called is True
    assert actual is True


@patch('StockBench.position.position.Position')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_intraday_percent_not_hit_case(data_mocker, position_mocker, test_object):
    # ============= Arrange ==============
    position_mocker.intraday_profit_loss_percent.return_value = -0.5

    # ============= Act ==================
    actual = test_object.check_trigger('stop_loss_intraday', '1%', data_mocker, position_mocker, 0)

    # ============= Assert ===============
    assert position_mocker.profit_loss_percent.called is True
    assert actual is False


@patch('StockBench.position.position.Position')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_intraday_hit_case(data_mocker, position_mocker, test_object):
    # ============= Arrange ==============
    position_mocker.intraday_profit_loss.return_value = -1500

    # ============= Act ==================
    actual = test_object.check_trigger('stop_loss_intraday', '1000', data_mocker, position_mocker, 0)

    # ============= Assert ===============
    assert position_mocker.profit_loss_percent.called is True
    assert actual is True


@patch('StockBench.position.position.Position')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_intraday_not_hit_case(data_mocker, position_mocker, test_object):
    # ============= Arrange ==============
    position_mocker.intraday_profit_loss.return_value = -150

    # ============= Act ==================
    actual = test_object.check_trigger('stop_loss_intraday', '1000', data_mocker, position_mocker, 0)

    # ============= Assert ===============
    assert position_mocker.profit_loss_percent.called is True
    assert actual is False


@patch('StockBench.position.position.Position')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_lifetime_percent_hit_case(data_mocker, position_mocker, test_object):
    # ============= Arrange ==============
    position_mocker.profit_loss_percent.return_value = -1.1

    # ============= Act ==================
    actual = test_object.check_trigger('stop_loss', '1%', data_mocker, position_mocker, 0)

    # ============= Assert ===============
    assert position_mocker.profit_loss_percent.called is True
    assert actual is True


@patch('StockBench.position.position.Position')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_lifetime_percent_not_hit_case(data_mocker, position_mocker, test_object):
    # ============= Arrange ==============
    position_mocker.profit_loss_percent.return_value = -0.1

    # ============= Act ==================
    actual = test_object.check_trigger('stop_loss', '1%', data_mocker, position_mocker, 0)

    # ============= Assert ===============
    assert position_mocker.profit_loss_percent.called is True
    assert actual is False


@patch('StockBench.position.position.Position')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_lifetime_hit_case(data_mocker, position_mocker, test_object):
    # ============= Arrange ==============
    position_mocker.profit_loss.return_value = -1500

    # ============= Act ==================
    actual = test_object.check_trigger('stop_loss', '1000', data_mocker, position_mocker, 0)

    # ============= Assert ===============
    assert position_mocker.profit_loss_percent.called is True
    assert actual is True


@patch('StockBench.position.position.Position')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_lifetime_not_hit_case(data_mocker, position_mocker, test_object):
    # ============= Arrange ==============
    position_mocker.profit_loss.return_value = -100

    # ============= Act ==================
    actual = test_object.check_trigger('stop_loss', '1000', data_mocker, position_mocker, 0)

    # ============= Assert ===============
    assert position_mocker.profit_loss_percent.called is True
    assert actual is False
