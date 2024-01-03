import os
import sys

# allows import out a directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


from plugins.volume.trigger import VolumeTrigger


# create test object
test_obj = VolumeTrigger('volume')


def test_additional_days():
    assert test_obj.additional_days('', '') == 0
