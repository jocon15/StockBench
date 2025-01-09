from unittest.mock import patch

from StockBench.indicator.trigger import Trigger
from StockBench.indicator.exceptions import StrategyIndicatorError
from StockBench.indicators.sma.trigger import SMATrigger


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


@patch('StockBench.simulation_data.data_manager.DataManager')
def test__parse_value(data_mocker):
    # ============= Arrange ==============
    data_mocker.get_data_point.return_value = 255.1
    test_object = Trigger('SMA', Trigger.BUY)

    # ============= Act ==================

    # ============= Assert ===============
    # normal case
    assert test_object._parse_rule_value('>250', data_mocker, 0) == ('>', 250.0)
    # current price in symbol case
    assert test_object._parse_rule_value('>$price', data_mocker, 0) == ('>', 255.1)
    # no number case
    try:
        test_object._parse_rule_value('>', data_mocker, 0)
        assert False
    except StrategyIndicatorError:
        assert True


def test_basic_trigger_check():
    # ============= Arrange ==============
    test_object = SMATrigger('SMA')

    # ============= Act ==================

    # ============= Assert ===============

    # gt true
    assert test_object.basic_trigger_check(200.0, '>150.0', None, 1) is True  # noqa
    # gt false
    assert test_object.basic_trigger_check(200.0, '>250.0', None, 1) is False  # noqa
    # lt true
    assert test_object.basic_trigger_check(100.0, '<150.0', None, 1) is True  # noqa
    # lt false
    assert test_object.basic_trigger_check(300.0, '<250.0', None, 1) is False  # noqa
    # gt eq true
    assert test_object.basic_trigger_check(300.0, '>=250.0', None, 1) is True  # noqa
    # gt eq false
    assert test_object.basic_trigger_check(200.0, '>=250.0', None, 1) is False  # noqa
    # lt eq true
    assert test_object.basic_trigger_check(200.0, '<=250.0', None, 1) is True  # noqa
    # lt eq false
    assert test_object.basic_trigger_check(300.0, '<=250.0', None, 1) is False  # noqa
    # eq true
    assert test_object.basic_trigger_check(200.0, '=200.0', None, 1) is True  # noqa
    # eq false
    assert test_object.basic_trigger_check(200.0, '=250.0', None, 1) is False  # noqa


def test_find_single_numeric_in_str():
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    # normal
    assert Trigger.find_single_numeric_in_str('SMA21') == 21

    # less than 1 number
    try:
        Trigger.find_single_numeric_in_str('SMA')
        assert False
    except StrategyIndicatorError:
        assert True

    # more than 1 number
    try:
        Trigger.find_single_numeric_in_str('SMA21$slope4')
        assert False
    except StrategyIndicatorError:
        assert True


def test_find_all_nums_in_str():
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert Trigger.find_all_nums_in_str('this thing') == []
    assert Trigger.find_all_nums_in_str('SMA21') == ['21']
    assert Trigger.find_all_nums_in_str('SMA21$slope12') == ['21', '12']


def test_find_operator_in_str():
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert Trigger.find_operator_in_str('>21') == '>'
    assert Trigger.find_operator_in_str('<=32') == '<='
    try:
        Trigger.find_operator_in_str('>')
        assert False
    except StrategyIndicatorError:
        assert True


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
    except StrategyIndicatorError:
        assert True
