from unittest.mock import MagicMock

import pytest
import requests

from StockBench.controllers.proxies.simulator_proxy import SimulatorProxy
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


STATUS_CODE = 'status_code'
MESSAGE = 'message'


# ================================= run_singular_simulation ============================================================


def test_run_singular_simulation_broker_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run.side_effect = requests.exceptions.ConnectionError

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_singular_simulation({}, '', 0.0, False, False,
                                                 mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Failed to connect to broker!'


def test_run_singular_simulation_malformed_strategy_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run.side_effect = MalformedStrategyError

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_singular_simulation({}, '', 0.0, False, False,
                                                 mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Malformed strategy error: '


def test_run_singular_simulation_strategy_indicator_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run.side_effect = StrategyIndicatorError

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_singular_simulation({}, '', 0.0, False, False,
                                                 mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Strategy error: '


def test_run_singular_simulation_missing_credential_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run.side_effect = MissingCredentialError

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_singular_simulation({}, '', 0.0, False, False,
                                                 mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Missing credential error: '


def test_run_singular_simulation_invalid_symbol_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run.side_effect = MissingCredentialError

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_singular_simulation({}, '', 0.0, False, False,
                                                 mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Missing credential error: '


def test_run_singular_simulation_insufficient_data_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run.side_effect = InsufficientDataError

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_singular_simulation({}, '', 0.0, False, False,
                                                 mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Insufficient data error: '


def test_run_singular_simulation_unexpected_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run.side_effect = ValueError  # a random error not explicitly caught by the decorator

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_singular_simulation({}, '', 0.0, False, False,
                                                 mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert 'Unexpected error: ' in result[MESSAGE]


def test_run_singular_simulation_normal_with_logging(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run.return_value = {'symbol': 'AAPL', 'avg_pl': 200.1, 'med_pl': 40.1}

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_singular_simulation({}, '', 0.0, True, False,
                                                 mock_progress_observer)

    # ============= Assert ===============
    mock_simulator.enable_logging.assert_called_once()
    mock_simulator.enable_reporting.assert_not_called()
    mock_simulator.set_initial_balance.assert_called_once_with(0.0)
    mock_simulator.load_strategy.assert_called_once_with({})

    assert type(result) is dict
    assert STATUS_CODE not in result.keys()
    assert result['symbol'] == 'AAPL'


def test_run_singular_simulation_normal_with_reporting(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run.return_value = {'symbol': 'AAPL', 'avg_pl': 200.1, 'med_pl': 40.1}

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_singular_simulation({}, '', 0.0, False, True,
                                                 mock_progress_observer)

    # ============= Assert ===============
    mock_simulator.enable_logging.assert_not_called()
    mock_simulator.enable_reporting.assert_called_once()
    mock_simulator.set_initial_balance.assert_called_once_with(0.0)
    mock_simulator.load_strategy.assert_called_once_with({})

    assert type(result) is dict
    assert STATUS_CODE not in result.keys()
    assert result['symbol'] == 'AAPL'


# ================================= run_multi_simulation ===============================================================

def test_run_multi_simulation_broker_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run_multiple.side_effect = requests.exceptions.ConnectionError

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_multi_simulation({}, [''], 0.0, False, False,
                                              mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Failed to connect to broker!'


def test_run_multi_simulation_malformed_strategy_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run_multiple.side_effect = MalformedStrategyError

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_multi_simulation({}, [''], 0.0, False, False,
                                              mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Malformed strategy error: '


def test_run_multi_simulation_strategy_indicator_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run_multiple.side_effect = StrategyIndicatorError

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_multi_simulation({}, [''], 0.0, False, False,
                                              mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Strategy error: '


def test_run_multi_simulation_missing_credential_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run_multiple.side_effect = MissingCredentialError

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_multi_simulation({}, [''], 0.0, False, False,
                                              mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Missing credential error: '


def test_run_multi_simulation_invalid_symbol_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run_multiple.side_effect = MissingCredentialError

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_multi_simulation({}, [''], 0.0, False, False,
                                              mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Missing credential error: '


def test_run_multi_simulation_insufficient_data_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run_multiple.side_effect = InsufficientDataError

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_multi_simulation({}, [''], 0.0, False, False,
                                              mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Insufficient data error: '


def test_run_multi_simulation_unexpected_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run_multiple.side_effect = ValueError  # a random error not explicitly caught by the decorator

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_multi_simulation({}, [''], 0.0, False, False,
                                              mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert 'Unexpected error: ' in result[MESSAGE]


def test_run_multi_simulation_normal_with_logging(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run_multiple.return_value = {'symbol': 'AAPL', 'avg_pl': 200.1, 'med_pl': 40.1}

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_multi_simulation({}, [''], 0.0, True, False,
                                              mock_progress_observer)

    # ============= Assert ===============
    mock_simulator.enable_logging.assert_called_once()
    mock_simulator.enable_reporting.assert_not_called()
    mock_simulator.set_initial_balance.assert_called_once_with(0.0)
    mock_simulator.load_strategy.assert_called_once_with({})

    assert type(result) is dict
    assert STATUS_CODE not in result.keys()
    assert result['symbol'] == 'AAPL'


def test_run_multi_simulation_normal_with_reporting(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run_multiple.return_value = {'symbol': 'AAPL', 'avg_pl': 200.1, 'med_pl': 40.1}

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_multi_simulation({}, [''], 0.0, False, True,
                                              mock_progress_observer)

    # ============= Assert ===============
    mock_simulator.enable_logging.assert_not_called()
    mock_simulator.enable_reporting.assert_called_once()
    mock_simulator.set_initial_balance.assert_called_once_with(0.0)
    mock_simulator.load_strategy.assert_called_once_with({})

    assert type(result) is dict
    assert STATUS_CODE not in result.keys()
    assert result['symbol'] == 'AAPL'


# ================================= run_folder_simulation ==============================================================


def test_run_folder_simulation_broker_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run_multiple.side_effect = requests.exceptions.ConnectionError

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_folder_simulation([{}, {}], ['', ''], 0.0, False, False,
                                               mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Failed to connect to broker!'


def test_run_folder_simulation_malformed_strategy_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run_multiple.side_effect = MalformedStrategyError

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_folder_simulation([{}, {}], ['', ''], 0.0, False, False,
                                               mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Malformed strategy error: '


def test_run_folder_simulation_strategy_indicator_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run_multiple.side_effect = StrategyIndicatorError

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_folder_simulation([{}, {}], ['', ''], 0.0, False, False,
                                               mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Strategy error: '


def test_run_folder_simulation_missing_credential_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run_multiple.side_effect = MissingCredentialError

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_folder_simulation([{}, {}], ['', ''], 0.0, False, False,
                                               mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Missing credential error: '


def test_run_folder_simulation_invalid_symbol_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run_multiple.side_effect = MissingCredentialError

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_folder_simulation([{}, {}], ['', ''], 0.0, False, False,
                                               mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Missing credential error: '


def test_run_folder_simulation_insufficient_data_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run_multiple.side_effect = InsufficientDataError

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_folder_simulation([{}, {}], ['', ''], 0.0, False, False,
                                               mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Insufficient data error: '


def test_run_folder_simulation_unexpected_error(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run_multiple.side_effect = ValueError  # a random error not explicitly caught by the decorator

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_folder_simulation([{}, {}], ['', ''], 0.0, False, False,
                                               mock_progress_observer)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert 'Unexpected error: ' in result[MESSAGE]


def test_run_folder_simulation_normal_with_logging(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run_multiple.return_value = {'symbol': 'AAPL', 'avg_pl': 200.1, 'med_pl': 40.1}

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_folder_simulation([{}, {}], ['', ''], 0.0, True, False,
                                               [mock_progress_observer, mock_progress_observer])

    # ============= Assert ===============
    mock_simulator.enable_logging.assert_called_once()
    mock_simulator.enable_reporting.assert_not_called()
    mock_simulator.set_initial_balance.assert_called_once_with(0.0)
    assert mock_simulator.load_strategy.call_count == 2

    assert type(result) is dict
    assert STATUS_CODE not in result.keys()
    assert type(result['results']) is list
    assert result['results'][0]['symbol'] == 'AAPL'


def test_run_folder_simulation_normal_with_reporting(mock_simulator, mock_progress_observer):
    # ============= Arrange ==============
    mock_simulator.run_multiple.return_value = {'symbol': 'AAPL', 'avg_pl': 200.1, 'med_pl': 40.1}

    test_object = SimulatorProxy(mock_simulator)

    # ============= Act ==================
    result = test_object.run_folder_simulation([{}, {}], ['', ''], 0.0, False, True,
                                               [mock_progress_observer, mock_progress_observer])

    # ============= Assert ===============
    mock_simulator.enable_logging.assert_not_called()
    mock_simulator.enable_reporting.assert_called_once()
    mock_simulator.set_initial_balance.assert_called_once_with(0.0)
    assert mock_simulator.load_strategy.call_count == 2

    assert type(result) is dict
    assert STATUS_CODE not in result.keys()
    assert type(result['results']) is list
    assert result['results'][0]['symbol'] == 'AAPL'
