from StockBench.triggers.trigger_manager import TriggerManager
import pytest


@pytest.fixture
def trigger_api():
    return TriggerManager({
        # FIXME: strategy goes here
    })


def test_check_buy_triggers(trigger_api):
    pass


def test_check_sell_triggers(trigger_api):
    pass
