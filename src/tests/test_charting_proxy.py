from unittest.mock import MagicMock

import pytest
from pandas import DataFrame

from StockBench.controllers.charting.exceptions import ChartingError
from StockBench.controllers.proxies.charting_proxy import ChartingProxy
from StockBench.models.constants.chart_filepath_key_constants import *
from StockBench.models.constants.simulation_results_constants import *


@pytest.fixture
def mock_singular_charting_engine():
    """Sets up a mocked simulator object."""
    return MagicMock()


@pytest.fixture
def mock_multi_charting_engine():
    """Sets up a mocked simulator object."""
    return MagicMock()


@pytest.fixture
def mock_folder_charting_engine():
    """Sets up a mocked simulator object."""
    return MagicMock()


STATUS_CODE = 'status_code'
MESSAGE = 'message'


# ================================= build_singular_charts ============================================================


def test_build_singular_charts_charting_error(mock_singular_charting_engine, mock_multi_charting_engine,
                                              mock_folder_charting_engine):
    # ============= Arrange ==============
    mock_singular_charting_engine.build_singular_overview_chart.side_effect = ChartingError

    test_object = ChartingProxy(mock_singular_charting_engine, mock_multi_charting_engine, mock_folder_charting_engine)

    # ============= Act ==================
    result = test_object.build_singular_charts({
        NORMALIZED_SIMULATION_DATA: None,
        SYMBOL_KEY: None,
        AVAILABLE_INDICATORS: None
    }, False, 0, False)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Charting error: '
    assert result[OVERVIEW_CHART_FILEPATH_KEY] == ''


def test_build_singular_charts_unexpected_error(mock_singular_charting_engine, mock_multi_charting_engine,
                                                mock_folder_charting_engine):
    # ============= Arrange ==============
    # a random error not explicitly caught by the decorator
    mock_singular_charting_engine.build_singular_overview_chart.side_effect = ValueError

    test_object = ChartingProxy(mock_singular_charting_engine, mock_multi_charting_engine, mock_folder_charting_engine)

    # ============= Act ==================
    result = test_object.build_singular_charts({
        NORMALIZED_SIMULATION_DATA: None,
        SYMBOL_KEY: None,
        AVAILABLE_INDICATORS: None
    }, False, 0, False)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert 'Unexpected error: ' in result[MESSAGE]
    assert result[OVERVIEW_CHART_FILEPATH_KEY] == ''


def test_build_singular_charts_normal_with_unique_chart_saving(mock_singular_charting_engine,
                                                               mock_multi_charting_engine,
                                                               mock_folder_charting_engine):
    # ============= Arrange ==============
    mock_singular_charting_engine.build_singular_overview_chart.return_value = 'filepath'
    mock_singular_charting_engine.build_account_value_line_chart.return_value = 'filepath'
    mock_singular_charting_engine.build_rules_bar_chart.return_value = 'filepath'
    mock_singular_charting_engine.build_positions_duration_bar_chart.return_value = 'filepath'
    mock_singular_charting_engine.build_positions_profit_loss_bar_chart.return_value = 'filepath'
    mock_singular_charting_engine.build_single_strategy_result_dataset_positions_plpc_histogram_chart.return_value = \
        'filepath'
    mock_singular_charting_engine.build_single_strategy_result_dataset_positions_plpc_box_plot.return_value = 'filepath'

    test_object = ChartingProxy(mock_singular_charting_engine, mock_multi_charting_engine, mock_folder_charting_engine)
    normalized_sim_data = DataFrame()
    normalized_sim_data['Account Value'] = []

    # ============= Act ==================
    result = test_object.build_singular_charts({
        NORMALIZED_SIMULATION_DATA: normalized_sim_data,
        SYMBOL_KEY: None,
        STRATEGY_KEY: None,
        AVAILABLE_INDICATORS: None,
        POSITIONS_KEY: None
    }, True, 0, False)

    # ============= Assert ===============
    assert type(result) is dict
    assert result == {
        OVERVIEW_CHART_FILEPATH_KEY: 'filepath',
        ACCOUNT_VALUE_LINE_CHART_FILEPATH_KEY: 'filepath',
        BUY_RULES_BAR_CHART_FILEPATH_KEY: 'filepath',
        SELL_RULES_BAR_CHART_FILEPATH_KEY: 'filepath',
        POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY: 'filepath',
        POSITIONS_PL_BAR_CHART_FILEPATH_KEY: 'filepath',
        POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH_KEY: 'filepath',
        POSITIONS_PLPC_BOX_PLOT_CHART_FILEPATH_KEY: 'filepath'
    }


def test_build_singular_charts_normal_without_results_depth_chart_saving(mock_singular_charting_engine,
                                                                         mock_multi_charting_engine,
                                                                         mock_folder_charting_engine):
    # ============= Arrange ==============
    test_object = ChartingProxy(mock_singular_charting_engine, mock_multi_charting_engine, mock_folder_charting_engine)

    # ============= Act ==================
    result = test_object.build_singular_charts({}, False, 1, False)

    # ============= Assert ===============
    assert type(result) is dict
    assert result == ChartingProxy.SINGULAR_DEFAULT_CHART_FILEPATHS


# ================================= build_multi_charts ===============================================================


def test_build_multi_charts_charting_error(mock_singular_charting_engine, mock_multi_charting_engine,
                                           mock_folder_charting_engine):
    # ============= Arrange ==============
    mock_multi_charting_engine.build_multi_overview_chart.side_effect = ChartingError

    test_object = ChartingProxy(mock_singular_charting_engine, mock_multi_charting_engine, mock_folder_charting_engine)

    # ============= Act ==================
    result = test_object.build_multi_charts({
        INDIVIDUAL_RESULTS_KEY: None,
        INITIAL_ACCOUNT_VALUE_KEY: None
    }, False, 0)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Charting error: '
    assert result[OVERVIEW_CHART_FILEPATH_KEY] == ''


def test_build_multi_charts_unexpected_error(mock_singular_charting_engine, mock_multi_charting_engine,
                                             mock_folder_charting_engine):
    # ============= Arrange ==============
    # a random error not explicitly caught by the decorator
    mock_multi_charting_engine.build_multi_overview_chart.side_effect = ValueError

    test_object = ChartingProxy(mock_singular_charting_engine, mock_multi_charting_engine, mock_folder_charting_engine)

    # ============= Act ==================
    result = test_object.build_multi_charts({
        INDIVIDUAL_RESULTS_KEY: None,
        INITIAL_ACCOUNT_VALUE_KEY: None
    }, False, 0)

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert 'Unexpected error: ' in result[MESSAGE]
    assert result[OVERVIEW_CHART_FILEPATH_KEY] == ''


def test_build_multi_charts_normal_with_unique_chart_saving(mock_singular_charting_engine,
                                                            mock_multi_charting_engine,
                                                            mock_folder_charting_engine):
    # ============= Arrange ==============
    mock_multi_charting_engine.build_multi_overview_chart.return_value = 'filepath'
    mock_multi_charting_engine.build_rules_bar_chart.return_value = 'filepath'
    mock_multi_charting_engine.build_positions_duration_bar_chart.return_value = 'filepath'
    mock_multi_charting_engine.build_positions_profit_loss_bar_chart.return_value = 'filepath'
    mock_multi_charting_engine.build_single_strategy_result_dataset_positions_plpc_histogram_chart.return_value = \
        'filepath'
    mock_multi_charting_engine.build_single_strategy_result_dataset_positions_plpc_box_plot.return_value = 'filepath'

    test_object = ChartingProxy(mock_singular_charting_engine, mock_multi_charting_engine, mock_folder_charting_engine)
    normalized_sim_data = DataFrame()
    normalized_sim_data['Account Value'] = []

    # ============= Act ==================
    result = test_object.build_multi_charts({
        INDIVIDUAL_RESULTS_KEY: None,
        INITIAL_ACCOUNT_VALUE_KEY: None,
        STRATEGY_KEY: None,
        POSITIONS_KEY: None
    }, True, 0)

    # ============= Assert ===============
    assert type(result) is dict
    assert result == {
        OVERVIEW_CHART_FILEPATH_KEY: 'filepath',
        BUY_RULES_BAR_CHART_FILEPATH_KEY: 'filepath',
        SELL_RULES_BAR_CHART_FILEPATH_KEY: 'filepath',
        POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY: 'filepath',
        POSITIONS_PL_BAR_CHART_FILEPATH_KEY: 'filepath',
        POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH_KEY: 'filepath',
        POSITIONS_PLPC_BOX_PLOT_CHART_FILEPATH_KEY: 'filepath'
    }


def test_build_multi_charts_normal_without_results_depth_chart_saving(mock_singular_charting_engine,
                                                                      mock_multi_charting_engine,
                                                                      mock_folder_charting_engine):
    # ============= Arrange ==============
    test_object = ChartingProxy(mock_singular_charting_engine, mock_multi_charting_engine, mock_folder_charting_engine)

    # ============= Act ==================
    result = test_object.build_multi_charts({}, False, 1)

    # ============= Assert ===============
    assert type(result) is dict
    assert result == ChartingProxy.MULTI_DEFAULT_CHART_FILEPATHS


# ================================= build_folder_charts ===============================================================


def test_build_folder_charts_charting_error(mock_singular_charting_engine, mock_multi_charting_engine,
                                            mock_folder_charting_engine):
    # ============= Arrange ==============
    mock_folder_charting_engine.build_trades_made_bar_chart.side_effect = ChartingError

    test_object = ChartingProxy(mock_singular_charting_engine, mock_multi_charting_engine, mock_folder_charting_engine)

    # ============= Act ==================
    result = test_object.build_folder_charts([])

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert result[MESSAGE] == 'Charting error: '
    assert result[TRADES_MADE_BAR_CHART_FILEPATH_KEY] == ''


def test_build_folder_charts_unexpected_error(mock_singular_charting_engine, mock_multi_charting_engine,
                                              mock_folder_charting_engine):
    # ============= Arrange ==============
    # a random error not explicitly caught by the decorator
    mock_folder_charting_engine.build_trades_made_bar_chart.side_effect = ValueError

    test_object = ChartingProxy(mock_singular_charting_engine, mock_multi_charting_engine, mock_folder_charting_engine)

    # ============= Act ==================
    result = test_object.build_folder_charts([])

    # ============= Assert ===============
    assert type(result) is dict
    assert result[STATUS_CODE] == 400
    assert 'Unexpected error: ' in result[MESSAGE]
    assert result[TRADES_MADE_BAR_CHART_FILEPATH_KEY] == ''


def test_build_folder_charts_normal(mock_singular_charting_engine, mock_multi_charting_engine,
                                    mock_folder_charting_engine):
    # ============= Arrange ==============
    mock_folder_charting_engine.build_trades_made_bar_chart.return_value = 'filepath'
    mock_folder_charting_engine.build_effectiveness_bar_chart.return_value = 'filepath'
    mock_folder_charting_engine.build_total_pl_bar_chart.return_value = 'filepath'
    mock_folder_charting_engine.build_average_pl_bar_chart.return_value = 'filepath'
    mock_folder_charting_engine.build_median_pl_bar_chart.return_value = 'filepath'
    mock_folder_charting_engine.build_stddev_pl_bar_chart.return_value = 'filepath'
    mock_folder_charting_engine.build_positions_plpc_histogram_chart.return_value = 'filepath'
    mock_folder_charting_engine.build_positions_plpc_box_chart.return_value = 'filepath'

    test_object = ChartingProxy(mock_singular_charting_engine, mock_multi_charting_engine, mock_folder_charting_engine)

    # ============= Act ==================
    result = test_object.build_folder_charts([])

    # ============= Assert ===============
    assert type(result) is dict
    assert result == {
        TRADES_MADE_BAR_CHART_FILEPATH_KEY: 'filepath',
        EFFECTIVENESS_BAR_CHART_FILEPATH_KEY: 'filepath',
        TOTAL_PL_BAR_CHART_FILEPATH_KEY: 'filepath',
        AVERAGE_PL_BAR_CHART_FILEPATH_KEY: 'filepath',
        MEDIAN_PL_BAR_CHART_FILEPATH_KEY: 'filepath',
        STDDEV_PL_BAR_CHART_FILEPATH_KEY: 'filepath',
        POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH_KEY: 'filepath',
        POSITIONS_PLPC_BOX_PLOT_CHART_FILEPATH_KEY: 'filepath'
    }
