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


def test_singular_simulation_normal(mock_simulator_proxy, mock_charting_proxy, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator_proxy.run_singular_simulation.return_value = {'results': 'example_results'}
    mock_charting_proxy.build_singular_charts.return_value = {'chart_filepath': 'example_filepath'}

    test_object = StockBenchController(mock_simulator_proxy, mock_charting_proxy)

    # ============= Act ==================
    result = test_object.singular_simulation({}, '', 0.0, False, False, False, 0, False, mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is SimulationResult
    assert result.status_code == 200
    assert result.message == ''
    assert result.simulation_results['results'] == 'example_results'
    assert result.chart_filepaths['chart_filepath'] == 'example_filepath'


# ================================= multi_simulation ================================================================

def test_multi_simulation_simulation_error(mock_simulator_proxy, mock_charting_proxy, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator_proxy.run_multi_simulation.return_value = {'status_code': 400, 'message': 'Unexpected error: '}

    test_object = StockBenchController(mock_simulator_proxy, mock_charting_proxy)

    # ============= Act ==================
    result = test_object.multi_simulation({}, [], 0.0, False, False, False, 0, mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is SimulationResult
    assert result.status_code == 400
    assert result.message == 'Unexpected error: '
    assert result.simulation_results == {}
    assert result.chart_filepaths == ChartingProxy.MULTI_DEFAULT_CHART_FILEPATHS


def test_multi_simulation_charting_error(mock_simulator_proxy, mock_charting_proxy, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator_proxy.run_multi_simulation.return_value = {'results': 'example_results'}
    mock_charting_proxy.build_multi_charts.return_value = \
        {'status_code': 400, 'message': 'Charting error: '}

    test_object = StockBenchController(mock_simulator_proxy, mock_charting_proxy)

    # ============= Act ==================
    result = test_object.multi_simulation({}, [], 0.0, False, False, False, 0, mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is SimulationResult
    assert result.status_code == 400
    assert result.message == 'Charting error: '
    assert result.simulation_results == {}
    assert result.chart_filepaths == ChartingProxy.MULTI_DEFAULT_CHART_FILEPATHS


def test_multi_simulation_normal(mock_simulator_proxy, mock_charting_proxy, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator_proxy.run_multi_simulation.return_value = {'results': 'example_results'}
    mock_charting_proxy.build_multi_charts.return_value = {'chart_filepath': 'example_filepath'}

    test_object = StockBenchController(mock_simulator_proxy, mock_charting_proxy)

    # ============= Act ==================
    result = test_object.multi_simulation({}, [], 0.0, False, False, False, 0, mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is SimulationResult
    assert result.status_code == 200
    assert result.message == ''
    assert result.simulation_results['results'] == 'example_results'
    assert result.chart_filepaths['chart_filepath'] == 'example_filepath'


# ================================= folder_simulation ==============================================================

def test_folder_simulation_simulation_error(mock_simulator_proxy, mock_charting_proxy, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator_proxy.run_folder_simulation.return_value = {'status_code': 400, 'message': 'Unexpected error: '}

    test_object = StockBenchController(mock_simulator_proxy, mock_charting_proxy)

    # ============= Act ==================
    result = test_object.folder_simulation([], [], 0.0, False, False, mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is SimulationResult
    assert result.status_code == 400
    assert result.message == 'Unexpected error: '
    assert result.simulation_results == {}
    assert result.chart_filepaths == ChartingProxy.FOLDER_DEFAULT_CHART_FILEPATHS


def test_folder_simulation_charting_error(mock_simulator_proxy, mock_charting_proxy, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator_proxy.run_folder_simulation.return_value = {'results': 'example_results'}
    mock_charting_proxy.build_folder_charts.return_value = \
        {'status_code': 400, 'message': 'Charting error: '}

    test_object = StockBenchController(mock_simulator_proxy, mock_charting_proxy)

    # ============= Act ==================
    result = test_object.folder_simulation([], [], 0.0, False, False, mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is SimulationResult
    assert result.status_code == 400
    assert result.message == 'Charting error: '
    assert result.simulation_results == {}
    assert result.chart_filepaths == ChartingProxy.FOLDER_DEFAULT_CHART_FILEPATHS


def test_folder_simulation_normal(mock_simulator_proxy, mock_charting_proxy, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator_proxy.run_folder_simulation.return_value = {'results': 'example_results'}
    mock_charting_proxy.build_folder_charts.return_value = {'chart_filepath': 'example_filepath'}

    test_object = StockBenchController(mock_simulator_proxy, mock_charting_proxy)

    # ============= Act ==================
    result = test_object.folder_simulation([], [], 0.0, False, False, mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is SimulationResult
    assert result.status_code == 200
    assert result.message == ''
    assert result.simulation_results['results'] == 'example_results'
    assert result.chart_filepaths['chart_filepath'] == 'example_filepath'
