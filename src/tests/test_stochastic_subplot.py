import pytest
from pandas import DataFrame
from plotly.graph_objs import Scatter

from StockBench.controllers.simulator.indicator.exceptions import SimulationDataException
from StockBench.controllers.simulator.indicators.stochastic.subplot import StochasticSubplot

INDICATOR_KEYS = [
    'stochastic',
    '20stochastic',
    '30stochastic'
]

THRESHOLD_KEYS = [
    'stochastic_30',
    'stochastic20_40',
    'stochastic30_50'
]

INDICATOR_Y_VALUES = [
    [101.3, 104.5, 106.7],
    [102.3, 107.5, 108.7],
    [105.3, 108.5, 104.7]
]

THRESHOLD_Y_VALUES = [
    [30.0, 30.0, 30.0],
    [40.0, 40.0, 40.0],
    [50.0, 50.0, 50.0]
]


@pytest.fixture
def date_setup_df() -> DataFrame:
    df = DataFrame()
    df['Date'] = ['2021-09-07T00:00:00Z', '2021-09-07T00:00:00Z', '2021-09-07T00:00:00Z']
    return df


@pytest.fixture
def test_object() -> StochasticSubplot:
    return StochasticSubplot()


def test_get_subplot_one_primary_trace(test_object: StochasticSubplot, date_setup_df: DataFrame):
    date_setup_df[INDICATOR_KEYS[0]] = INDICATOR_Y_VALUES[0]

    # initial state
    assert len(test_object.remaining_traces) == 0

    result = test_object.get_subplot(date_setup_df)

    validate_scatter_trace(result, INDICATOR_KEYS[0], INDICATOR_Y_VALUES[0])
    assert len(test_object.remaining_traces) == 0


def test_get_subplot_three_primary_trace(test_object: StochasticSubplot, date_setup_df: DataFrame):
    date_setup_df[INDICATOR_KEYS[0]] = INDICATOR_Y_VALUES[0]
    date_setup_df[INDICATOR_KEYS[1]] = INDICATOR_Y_VALUES[1]
    date_setup_df[INDICATOR_KEYS[2]] = INDICATOR_Y_VALUES[2]

    # initial state
    assert len(test_object.remaining_traces) == 0

    result = test_object.get_subplot(date_setup_df)

    validate_scatter_trace(result, INDICATOR_KEYS[0], INDICATOR_Y_VALUES[0])
    assert len(test_object.remaining_traces) == 2
    for i, trace in enumerate(test_object.remaining_traces):
        validate_scatter_trace(trace, INDICATOR_KEYS[i + 1], INDICATOR_Y_VALUES[i + 1])


def test_get_subplot_zero_primary_trace_exception(test_object: StochasticSubplot, date_setup_df: DataFrame):
    # no stochastic traces added

    with pytest.raises(SimulationDataException):
        test_object.get_subplot(date_setup_df)


def test_get_traces_none_remaining_no_thresholds(test_object: StochasticSubplot, date_setup_df: DataFrame):
    result = test_object.get_traces(date_setup_df)

    assert len(result) == 0


def test_get_traces_two_remaining_two_thresholds(test_object: StochasticSubplot, date_setup_df: DataFrame):
    date_setup_df[INDICATOR_KEYS[0]] = INDICATOR_Y_VALUES[0]
    date_setup_df[INDICATOR_KEYS[1]] = INDICATOR_Y_VALUES[1]
    date_setup_df[INDICATOR_KEYS[2]] = INDICATOR_Y_VALUES[2]
    # thresholds
    date_setup_df[THRESHOLD_KEYS[0]] = THRESHOLD_Y_VALUES[0]
    date_setup_df[THRESHOLD_KEYS[1]] = THRESHOLD_Y_VALUES[1]

    # initial state
    assert len(test_object.remaining_traces) == 0

    result = test_object.get_subplot(date_setup_df)

    # intermediate state
    validate_scatter_trace(result, INDICATOR_KEYS[0], INDICATOR_Y_VALUES[0])
    assert len(test_object.remaining_traces) == 2

    second_result = test_object.get_traces(date_setup_df)

    assert len(second_result) == 4

    validate_scatter_trace(second_result[0], INDICATOR_KEYS[1], INDICATOR_Y_VALUES[1])
    validate_scatter_trace(second_result[1], INDICATOR_KEYS[2], INDICATOR_Y_VALUES[2])
    validate_scatter_trace(second_result[2], THRESHOLD_KEYS[0], THRESHOLD_Y_VALUES[0])
    validate_scatter_trace(second_result[3], THRESHOLD_KEYS[1], THRESHOLD_Y_VALUES[1])


def validate_scatter_trace(trace, name: str, y_values: list):
    assert isinstance(trace, Scatter)
    assert trace['name'] == name
    assert len(trace.y) == len(y_values)
    for i, value in enumerate(trace.y):
        assert value == y_values[i]
