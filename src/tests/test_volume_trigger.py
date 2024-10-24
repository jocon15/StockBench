from StockBench.indicators.volume.trigger import VolumeTrigger


# create test object
test_obj = VolumeTrigger('volume')


def test_additional_days():
    assert test_obj.additional_days('', '') == 0
