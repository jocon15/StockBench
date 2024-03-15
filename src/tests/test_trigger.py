import pytest
from unittest.mock import patch
from StockBench.triggers.trigger import Trigger


def test_get_side():
    # ============= Arrange ==============
    test_object_1 = Trigger('SMA', Trigger.BUY)
    test_object_2 = Trigger('SMA', Trigger.SELL)
    test_object_3 = Trigger('SMA', Trigger.AGNOSTIC)

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object_1.get_side() == Trigger.BUY
    assert test_object_2.get_side() == Trigger.SELL
    assert test_object_3.get_side() == Trigger.AGNOSTIC


def test__parse_value():
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    pass


def test_basic_trigger_check():
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    pass


def find_single_numeric_in_str():
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    # normal
    assert Trigger.find_single_numeric_in_str('SMA21') == 21

    # less than 1 number
    try:
        Trigger.find_single_numeric_in_str('SMA')
        assert False
    except ValueError:
        assert True

    # more than 1 number
    try:
        Trigger.find_single_numeric_in_str('SMA21$slope4')
        assert False
    except ValueError:
        assert True


def test_find_all_nums_in_str():
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert Trigger.find_all_nums_in_str('this thing') == []
    assert Trigger.find_all_nums_in_str('SMA21') == [21]
    assert Trigger.find_all_nums_in_str('SMA21$slope12') == [21, 12]


def test_find_operator_in_str():
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    pass


def test_calculate_slope():
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    # normal
    assert Trigger.calculate_slope(200, 100, 2) == 50.00
    assert Trigger.calculate_slope(400, 0, 4) == 100.00

    # bad length
    try:
        Trigger.calculate_slope(1, 2, 1)
        assert False
    except ValueError:
        assert True
