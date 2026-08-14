from StockBench.controllers.simulator.indicator.trigger_interface import TriggerInterface
from StockBench.controllers.simulator.indicator.exceptions import StrategyIndicatorError
from StockBench.controllers.simulator.indicators.sma.trigger import SMATrigger


def test_get_side():
    # ============= Arrange ==============
    test_object_1 = TriggerInterface('SMA', TriggerInterface.BUY)
    test_object_2 = TriggerInterface('SMA', TriggerInterface.SELL)
    test_object_3 = TriggerInterface('SMA', TriggerInterface.AGNOSTIC)

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object_1.get_side() == TriggerInterface.BUY
    assert test_object_2.get_side() == TriggerInterface.SELL
    assert test_object_3.get_side() == TriggerInterface.AGNOSTIC


def test_basic_trigger_check():
    # ============= Arrange ==============
    test_object = SMATrigger('SMA')

    # ============= Act ==================

    # ============= Assert ===============

    # gt true
    assert test_object.basic_trigger_check(200.0, '>150.0') is True
    # gt false
    assert test_object.basic_trigger_check(200.0, '>250.0') is False
    # lt true
    assert test_object.basic_trigger_check(100.0, '<150.0') is True
    # lt false
    assert test_object.basic_trigger_check(300.0, '<250.0') is False
    # gt eq true
    assert test_object.basic_trigger_check(300.0, '>=250.0') is True
    # gt eq false
    assert test_object.basic_trigger_check(200.0, '>=250.0') is False
    # lt eq true
    assert test_object.basic_trigger_check(200.0, '<=250.0') is True
    # lt eq false
    assert test_object.basic_trigger_check(300.0, '<=250.0') is False
    # eq true
    assert test_object.basic_trigger_check(200.0, '=200.0') is True
    # eq false
    assert test_object.basic_trigger_check(200.0, '=250.0') is False


def test_find_single_numeric_in_str():
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    # normal
    assert TriggerInterface.find_single_numeric_in_str('SMA21') == 21

    # less than 1 number
    try:
        TriggerInterface.find_single_numeric_in_str('SMA')
        assert False
    except StrategyIndicatorError:
        assert True

    # more than 1 number
    try:
        TriggerInterface.find_single_numeric_in_str('SMA21$slope4')
        assert False
    except StrategyIndicatorError:
        assert True


def test_find_all_nums_in_str():
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert TriggerInterface.find_all_nums_in_str('this thing') == []
    assert TriggerInterface.find_all_nums_in_str('SMA21') == ['21']
    assert TriggerInterface.find_all_nums_in_str('SMA21$slope12') == ['21', '12']


def test_find_operator_in_str():
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert TriggerInterface.find_operator_in_str('>21') == '>'
    assert TriggerInterface.find_operator_in_str('<=32') == '<='
    try:
        TriggerInterface.find_operator_in_str('>')
        assert False
    except StrategyIndicatorError:
        assert True
