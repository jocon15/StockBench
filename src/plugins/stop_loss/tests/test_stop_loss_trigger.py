import os
import sys

# allows import out a directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


from plugins.stop_loss.trigger import StopLossTrigger


# create test object
test_obj = StopLossTrigger('stop_loss')


def test_additional_days():
    assert test_obj.additional_days('', '') == 0
