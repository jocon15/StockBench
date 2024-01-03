import os
import sys
from unittest.mock import patch

# allows import from src directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from StockBench.plugins.price import PriceTrigger

test_object = PriceTrigger('price')


def test_additional_days():
    assert test_object.additional_days('none', '') == 0


def test_add_to_data():
    try:
        test_object.add_to_data('', '', '', None)
        assert True
    except Exception as e:
        assert False


@patch('StockBench.triggers.trigger.Trigger.find_numeric_in_str')
@patch('StockBench.triggers.trigger.Trigger.find_operator_in_str')
@patch('StockBench.triggers.trigger.Trigger.basic_triggers_check')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger(data_mocker, basic_trigger_mocker, operator_mocker, numeric_mocker):
    data_mocker.get_data_point.side_effect = None
    basic_trigger_mocker.return_value = False
    operator_mocker.return_value = None
    numeric_mocker.return_value = None

    # trigger not hit
    assert (test_object.check_trigger('$price', '>350', data_mocker, None, 2)
            is False)

    # trigger hit
    basic_trigger_mocker.return_value = True
    assert (test_object.check_trigger('$price', '>350', data_mocker, None, 2)
            is True)


@patch('StockBench.triggers.trigger.Trigger.find_numeric_in_str')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger_value_error(data_mocker, numeric_mocker):
    data_mocker.get_data_point.return_value = 90
    numeric_mocker.side_effect = value_error_side_effect

    # simple trigger not hit case
    assert test_object.check_trigger('EMA20$slope', '>60', data_mocker, None, 0) is False

def value_error_side_effect(*args):  # noqa
    raise ValueError()
