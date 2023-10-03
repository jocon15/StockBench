import os
import sys

# allows import out a directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


from plugins.rsi.trigger import RSITrigger


# create test object
test_obj = RSITrigger('MSFT')


def test_additional_days():
    assert test_obj.additional_days('RSI') == 14

    assert test_obj.additional_days('RSI50') == 50

    assert test_obj.additional_days('RSI50$price') == 50

    assert test_obj.additional_days('RSI20$slope10') == 20

    assert test_obj.additional_days('RSI20$slope30') == 30
