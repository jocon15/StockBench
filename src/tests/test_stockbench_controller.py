from unittest.mock import MagicMock

import pytest

from StockBench.controllers.proxies.charting_proxy import ChartingProxy
from StockBench.controllers.stockbench_controller import StockBenchController
from StockBench.models.simulation_result.simulation_result import SimulationResult


@pytest.fixture
def mock_simulator_proxy():
    return MagicMock()


@pytest.fixture
def mock_charting_proxy():
    return MagicMock()


@pytest.fixture
def mock_progress_observer():
    """Sets up a mocked progress observer object."""
    return MagicMock()


# ================================= singular_simulation ============================================================

def test_singular_simulation_simulation_error(mock_simulator_proxy, mock_charting_proxy, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator_proxy.run_singular_simulation.return_value = {'status_code': 400, 'message': 'Unexpected error: '}

    test_object = StockBenchController(mock_simulator_proxy, mock_charting_proxy)

    # ============= Act ==================
    result = test_object.singular_simulation({}, '', 0.0, False, False, False, 0, False, mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is SimulationResult
    assert result.status_code == 400
    assert result.message == 'Unexpected error: '
    assert result.simulation_results == {}
    assert result.chart_filepaths == ChartingProxy.SINGULAR_DEFAULT_CHART_FILEPATHS


def test_singular_simulation_charting_error(mock_simulator_proxy, mock_charting_proxy, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator_proxy.run_singular_simulation.return_value = {'results': 'example_results'}
    mock_charting_proxy.build_singular_charts.return_value = \
        {'status_code': 400, 'message': 'Charting error: '}

    test_object = StockBenchController(mock_simulator_proxy, mock_charting_proxy)

    # ============= Act ==================
    result = test_object.singular_simulation({}, '', 0.0, False, False, False, 0, False, mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is SimulationResult
    assert result.status_code == 400
    assert result.message == 'Charting error: '
    assert result.simulation_results == {}
    assert result.chart_filepaths == ChartingProxy.SINGULAR_DEFAULT_CHART_FILEPATHS
