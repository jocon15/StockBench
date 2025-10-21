from unittest.mock import MagicMock

import pytest
import requests

from StockBench.controllers.proxies.simulation_proxy import SimulationProxy
from StockBench.controllers.simulator.algorithm.exceptions import MalformedStrategyError
from StockBench.controllers.simulator.broker.broker_client import MissingCredentialError, InsufficientDataError
from StockBench.controllers.simulator.indicator.exceptions import StrategyIndicatorError


@pytest.fixture
def mock_simulator():
    """Sets up a mocked simulator object."""
    return MagicMock()


@pytest.fixture
def mock_progress_observer():
    """Sets up a mocked progress observer object."""
    return MagicMock()


def test_run_singular_simulation_broker_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run.side_effect = requests.exceptions.ConnectionError

    # ============= Act ==================
    result = SimulationProxy.run_singular_simulation(mock_simulator, {}, '', 0.0, False, False,
                                                     mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result['status_code'] == 400
    assert result['message'] == 'Failed to connect to broker!'


def test_run_singular_simulation_malformed_strategy_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run.side_effect = MalformedStrategyError

    # ============= Act ==================
    result = SimulationProxy.run_singular_simulation(mock_simulator, {}, '', 0.0, False, False,
                                                     mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result['status_code'] == 400
    assert result['message'] == 'Malformed strategy error: '


def test_run_singular_simulation_strategy_indicator_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run.side_effect = StrategyIndicatorError

    # ============= Act ==================
    result = SimulationProxy.run_singular_simulation(mock_simulator, {}, '', 0.0, False, False,
                                                     mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result['status_code'] == 400
    assert result['message'] == 'Strategy error: '


def test_run_singular_simulation_missing_credential_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run.side_effect = MissingCredentialError

    # ============= Act ==================
    result = SimulationProxy.run_singular_simulation(mock_simulator, {}, '', 0.0, False, False,
                                                     mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result['status_code'] == 400
    assert result['message'] == 'Missing credential error: '


def test_run_singular_simulation_invalid_symbol_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run.side_effect = MissingCredentialError

    # ============= Act ==================
    result = SimulationProxy.run_singular_simulation(mock_simulator, {}, '', 0.0, False, False,
                                                     mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result['status_code'] == 400
    assert result['message'] == 'Missing credential error: '


def test_run_singular_simulation_insufficient_data_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run.side_effect = InsufficientDataError

    # ============= Act ==================
    result = SimulationProxy.run_singular_simulation(mock_simulator, {}, '', 0.0, False, False,
                                                     mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result['status_code'] == 400
    assert result['message'] == 'Insufficient data error: '


def test_run_singular_simulation_unexpected_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run.side_effect = ValueError  # a random error not explicitly caught by the decorator

    # ============= Act ==================
    result = SimulationProxy.run_singular_simulation(mock_simulator, {}, '', 0.0, False, False,
                                                     mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result['status_code'] == 400
    assert 'Unexpected error: ' in result['message']


def test_run_singular_simulation_normal_with_logging(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run.return_value = {'symbol': 'AAPL', 'avg_pl': 200.1, 'med_pl': 40.1}

    # ============= Act ==================
    result = SimulationProxy.run_singular_simulation(mock_simulator, {}, '', 0.0, True, False,
                                                     mock_progress_observer)

    # ============= Assert ===============
    mock_simulator.enable_logging.assert_called_once()
    mock_simulator.enable_reporting.assert_not_called()
    mock_simulator.set_initial_balance.assert_called_once_with(0.0)
    mock_simulator.load_strategy.assert_called_once_with({})

    assert type(result) is dict
    assert 'status_code' not in result.keys()
    assert result['symbol'] == 'AAPL'


def test_run_singular_simulation_normal_with_reporting(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run.return_value = {'symbol': 'AAPL', 'avg_pl': 200.1, 'med_pl': 40.1}

    # ============= Act ==================
    result = SimulationProxy.run_singular_simulation(mock_simulator, {}, '', 0.0, False, True,
                                                     mock_progress_observer)

    # ============= Assert ===============
    mock_simulator.enable_logging.assert_not_called()
    mock_simulator.enable_reporting.assert_called_once()
    mock_simulator.set_initial_balance.assert_called_once_with(0.0)
    mock_simulator.load_strategy.assert_called_once_with({})

    assert type(result) is dict
    assert 'status_code' not in result.keys()
    assert result['symbol'] == 'AAPL'


# FIXME: need tests for run_multi_simulation() function

# FIXME: need tests for run_folder_simulation() function
