from StockBench.controllers.simulator.indicator.rule_interface import RuleInterface
from StockBench.controllers.simulator.indicator.exceptions import StrategyIndicatorError
from StockBench.controllers.simulator.indicators.sma.rule import SMARule


def test_get_side():
    # ============= Arrange ==============
    test_object_1 = RuleInterface('SMA', RuleInterface.BUY)
    test_object_2 = RuleInterface('SMA', RuleInterface.SELL)
    test_object_3 = RuleInterface('SMA', RuleInterface.AGNOSTIC)

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object_1.get_side() == RuleInterface.BUY
    assert test_object_2.get_side() == RuleInterface.SELL
    assert test_object_3.get_side() == RuleInterface.AGNOSTIC


def test_basic_trigger_check():
    # ============= Arrange ==============
    test_object = SMARule('SMA')

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
    assert RuleInterface.find_single_numeric_in_str('SMA21') == 21

    # less than 1 number
    try:
        RuleInterface.find_single_numeric_in_str('SMA')
        assert False
    except StrategyIndicatorError:
        assert True

    # more than 1 number
    try:
        RuleInterface.find_single_numeric_in_str('SMA21$slope4')
        assert False
    except StrategyIndicatorError:
        assert True


def test_find_all_nums_in_str():
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert RuleInterface.find_all_nums_in_str('this thing') == []
    assert RuleInterface.find_all_nums_in_str('SMA21') == ['21']
    assert RuleInterface.find_all_nums_in_str('SMA21$slope12') == ['21', '12']


def test_find_operator_in_str():
    # ============= Arrange ==============

    # ============= Act ==================

    # ============= Assert ===============
    assert RuleInterface.find_operator_in_str('>21') == '>'
    assert RuleInterface.find_operator_in_str('<=32') == '<='
    try:
        RuleInterface.find_operator_in_str('>')
        assert False
    except StrategyIndicatorError:
        assert True
