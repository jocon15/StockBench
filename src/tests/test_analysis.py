import pytest
from StockBench.position.position import Position
from StockBench.analysis.analyzer import SimulationAnalyzer


@pytest.fixture
def test_positions():
    # set up 3 positions to test
    pos_1 = Position(100, 10)
    pos_1.close_position(200)

    pos_2 = Position(50, 10)
    pos_2.close_position(175)

    pos_3 = Position(300, 10)
    pos_3.close_position(150)

    return [pos_1, pos_2, pos_3]


def test_total_trades(test_positions):
    # ============= Arrange ==============
    test_object = SimulationAnalyzer(test_positions)

    # ============= Act ==================
    actual = test_object.total_trades()

    # ============= Assert ===============
    assert type(actual) is int
    assert actual == 3


def test_effectiveness_normal(test_positions):
    # ============= Arrange ==============
    test_object = SimulationAnalyzer(test_positions)

    # ============= Act ==================
    actual = test_object.effectiveness()

    # ============= Assert ===============
    assert type(actual) is float
    assert int(actual) == 66


def test_effectiveness_empty():
    # ============= Arrange ==============
    test_object = SimulationAnalyzer([])

    # ============= Act ==================

    # ============= Assert ===============
    assert int(test_object.effectiveness()) == 0


def test_total_profit_loss(test_positions):
    # ============= Arrange ==============
    test_object = SimulationAnalyzer(test_positions)

    # ============= Act ==================
    actual = test_object.total_profit_loss()

    # ============= Assert ===============
    assert type(actual) is float
    assert actual == 750.0


def test_average_profit_loss_normal(test_positions):
    # ============= Arrange ==============
    test_object = SimulationAnalyzer(test_positions)

    # ============= Act ==================
    actual = test_object.average_profit_loss()

    # ============= Assert ===============
    assert type(actual) is float
    assert actual == 250.0


def test_average_profit_loss_empty():
    # ============= Arrange ==============
    test_object = SimulationAnalyzer([])

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.average_profit_loss() == 0.0


def test_median_profit_loss_normal(test_positions):
    # ============= Arrange ==============
    test_object = SimulationAnalyzer(test_positions)

    # ============= Act ==================
    actual = test_object.median_profit_loss()

    # ============= Assert ===============
    assert type(actual) is float
    assert actual == 1000.0


def test_median_profit_loss_empty():
    # ============= Arrange ==============
    test_object = SimulationAnalyzer([])

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.median_profit_loss() == 0.0


def test_standard_profit_loss_deviation_normal(test_positions):
    # ============= Arrange ==============
    test_object = SimulationAnalyzer(test_positions)

    # ============= Act ==================
    actual = test_object.standard_profit_loss_deviation()

    # ============= Assert ===============
    assert type(actual) is float
    assert int(actual) == 1241


def test_standard_profit_loss_deviation_empty():
    # ============= Arrange ==============
    test_object = SimulationAnalyzer([])

    # ============= Act ==================

    # ============= Assert ===============
    assert test_object.standard_profit_loss_deviation() == 0.0
