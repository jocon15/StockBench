import os
import sys
from unittest.mock import patch
from tests.example_data.ExampleBarsData import EXAMPLE_DATA_MSFT

# allows import out a directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


from StockBench.plugins.rsi.trigger import RSITrigger


# create test object
test_obj = RSITrigger('RSI')


def test_additional_days():
    assert test_obj.additional_days('RSI', '>20') == 14

    assert test_obj.additional_days('RSI50', '>20') == 50

    assert test_obj.additional_days('RSI50$price', '>20') == 50

    assert test_obj.additional_days('RSI20$slope10', '>20') == 20

    assert test_obj.additional_days('RSI20$slope30', '>20') == 30


@patch('logging.getLogger')
@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_additional_days(data_mocker, logger_mocker):
    logger_mocker.return_value = logger_mocker
    logger_mocker.warning.side_effect = logger_side_effect

    data_mocker.add_column.side_effect = add_column_side_effect

    # assemble a price list from the example data
    price_data = []
    for day in EXAMPLE_DATA_MSFT['MSFT']:
        price_data.append(float(day['o']))

    data_mocker.get_column_data.return_value = price_data
    data_mocker.get_column_nmes.return_value = []

    # test normal case
    test_obj.add_to_data('RSI', '>30', 'buy', data_mocker)
    # assertions are done in side effect function

    # test console output if no indicator length is provided
    test_obj.add_to_data('RSI', '>30', 'buy', data_mocker)
    # assertions are done in side effect function


def logger_side_effect(*args):
    if args[0] == 'Warning: RSI is in incorrect format and will be ignored':
        assert True
    else:
        assert False


def add_column_side_effect(*args):
    assert args[0] == 'RSI'
    # FIXME: get RSI test data for test data
    assert args[1] == []