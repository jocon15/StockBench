import os
import sys
from unittest.mock import patch

# allows import out a directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from StockBench.plugins.candlestick_color.trigger import CandlestickColorTrigger

# create test object
test_obj = CandlestickColorTrigger('color')


def test_additional_days():
    assert test_obj.additional_days('', '') == 0
    # FIXME: needs additional testing now that candlestick has the ability to use value to calculate additonal days


def test_add_to_data():
    # add data for candlestick trigger should just return
    try:
        test_obj.add_to_data('', '', '', None)
        assert True
    except Exception as e:
        print(e)
        assert False


@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger(data_mocker):
    current_day_index = 0

    data_mocker.COLOR = "color"
    data_mocker.get_data_point.side_effect = mock_colors_even

    assert test_obj.check_trigger('color',
                                  {'0': 'green', '1': 'red'},
                                  data_mocker,
                                  None,
                                  current_day_index) is True

    assert test_obj.check_trigger('color',
                                  {'0': 'red', '1': 'green'},
                                  data_mocker,
                                  None,
                                  current_day_index) is False


def mock_colors_even(*args):
    if args[1] % 2 == 0:
        return 'green'
    else:
        return 'red'
