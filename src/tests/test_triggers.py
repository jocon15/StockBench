from StockBench.triggers.triggering_api import TriggerAPI
import pytest


@pytest.fixture
def trigger_api():
    return TriggerAPI({
        # FIXME: strategy goes here
    })


def test_check_buy_triggers(trigger_api):
    pass


def test_check_sell_triggers(trigger_api):
    pass
