import os
import sys

# allows import out a directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


from plugins.ema.trigger import EMATrigger


# create test object
test_obj = EMATrigger('MSFT')


def test_additional_days():
    assert test_obj.additional_days('EMA20') == 20

    assert test_obj.additional_days('EMA50$price') == 50

    assert test_obj.additional_days('EMA50$price') == 50

    assert test_obj.additional_days('EMA20$slope10') == 20

    assert test_obj.additional_days('EMA20$slope30') == 30
