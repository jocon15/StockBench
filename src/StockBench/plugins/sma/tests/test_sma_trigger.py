import os
import sys

# allows import out a directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


from plugins.sma.trigger import SMATrigger


# create test object
test_obj = SMATrigger('SMA')


def test_additional_days():
    assert test_obj.additional_days('SMA20', '>20') == 20

    assert test_obj.additional_days('SMA50$price', '>20') == 50

    assert test_obj.additional_days('SMA50$price', '>20') == 50

    assert test_obj.additional_days('SMA20$slope10', '>20') == 20

    assert test_obj.additional_days('SMA20$slope30', '>20') == 30
