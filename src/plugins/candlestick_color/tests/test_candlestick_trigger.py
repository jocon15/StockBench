import os
import sys
from unittest.mock import patch

# allows import out a directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from plugins.candlestick_color.trigger import CandlestickColorTrigger

# create test object
test_obj = CandlestickColorTrigger('color')


def test_additional_days():
    assert test_obj.additional_days('') == 0


@patch('StockBench.simulation_data.data_manager.DataManager')
def test_check_trigger(data_mocker):
    current_day_index = 0

    data_mocker.COLOR = "color"
    data_mocker.get_data_point.side_effect = mock_side_effect

    assert test_obj.check_trigger('color',
                                  {'0': 'green', '1': 'red'},
                                  data_mocker,
                                  None,
                                  current_day_index) is True


def mock_side_effect(*args):
    if args[1] % 2 == 0:
        return 'green'
    else:
        return 'red'
