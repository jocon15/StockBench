import json
import time
import requests
from unittest.mock import patch, Mock
from requests.models import Response
from StockBench.broker.broker_client import BrokerClient, InvalidSymbolError, MissingCredentialError
from tests.example_data.ExampleBarsData import EXAMPLE_UN_KEYED_MSFT
from tests.example_data.ExampleAPIData import ORDER_DATA, BAD_ORDER_DATA, CLOSE_DATA

# setup mock credentials
mock_config = Mock()
mock_config.api_public_key.return_value = 'Pretend Key'
mock_config.api_secret_key.return_value = 'Pretend Key'

# set up an instance of the broker to test
test_object = BrokerClient(mock_config)

# setting up the response object that we are hijacking with
the_response = Response()
the_response.code = "200"
the_response.error_type = ""
the_response.status_code = 200
the_response._content = b'{ "key" : "a" }'

# ======================= 400 Response =======================
api_400_response = Response()
api_400_response.code = "400"
api_400_response.error_type = "That didn't work"
api_400_response.status_code = 400
api_400_response._content = b'{ "key" : "a" }'
# =========================================================================

# ======================= 200 Bars Data =======================
api_200_response = Response()
api_200_response.code = "200"
api_200_response.error_type = "That worked!"
api_200_response.status_code = 200
api_200_response._content = json.dumps(EXAMPLE_UN_KEYED_MSFT, indent=2).encode('utf-8')
# =========================================================================

# ======================= 200 EMPTY Bars Data =======================
api_200_EMPTY_response = Response()
api_200_EMPTY_response.code = "200"
api_200_EMPTY_response.error_type = "That worked!"
api_200_EMPTY_response.status_code = 200
api_200_EMPTY_response._content = json.dumps({'bars': {}}, indent=2).encode('utf-8')
# =========================================================================

# ======================= 200 Order Data =======================
api_200_order_response = Response()
api_200_order_response.code = "200"
api_200_order_response.error_type = "That worked!"
api_200_order_response.status_code = 200
api_200_order_response._content = json.dumps(ORDER_DATA, indent=2).encode('utf-8')
# =========================================================================

# ======================= 401 Order Data =======================
api_401_order_response = Response()
api_401_order_response.code = "401"
api_401_order_response.error_type = "That did not work!"
api_401_order_response.status_code = 401
api_401_order_response._content = json.dumps(BAD_ORDER_DATA, indent=2).encode('utf-8')
# =========================================================================

# ======================= 200 Close Data =======================
api_200_close_response = Response()
api_200_close_response.code = "200"
api_200_close_response.error_type = "That worked!"
api_200_close_response.status_code = 200
api_200_close_response._content = json.dumps(CLOSE_DATA, indent=2).encode('utf-8')
# =========================================================================

# ======================= 401 Close Data =======================
api_401_close_response = Response()
api_401_close_response.code = "401"
api_401_close_response.error_type = "That did not work!"
api_401_close_response.status_code = 401
api_401_close_response._content = json.dumps(BAD_ORDER_DATA, indent=2).encode('utf-8')  # uses same bad data as order
# =========================================================================


def test_constructor_missing_public_key():
    """Test broker client config to ensure the correct error is thrown."""
    # ================================= Arrange ================================
    mock_bad_config = Mock()
    mock_bad_config.public_key = None

    # ================================= Act ====================================

    # ================================= Assert =================================
    try:
        BrokerClient(mock_bad_config)
        assert False
    except MissingCredentialError:
        assert True


def test_constructor_missing_private_key():
    """Test broker client config to ensure the correct error is thrown."""
    # ================================= Arrange ================================
    mock_bad_config = Mock()
    mock_bad_config.public_key = 'not none'
    mock_bad_config.private_key = None

    # ================================= Act ====================================

    # ================================= Assert =================================
    try:
        BrokerClient(mock_bad_config)
        assert False
    except MissingCredentialError:
        assert True


@patch('requests.get')
def test_get_bars_data(mocker):
    """Test get_bars_data to ensure it returns data in the correct format."""
    # ================================= Arrange ================================
    # for some reason, this 1-stop-shop way of doing it is the only way that works
    # for setting up the status code to correctly return the status code defined in
    # the response object
    mocker.return_value = mocker
    mocker.return_value.status_code = api_200_response.status_code
    mocker.json.return_value = api_200_response.json()

    # unix dates don't matter because the data is mocked, but we do this to simulate
    # actual unix values used as parameters
    unix_now = 1693530000  # end timestamp the MSFT test data uses
    unix_past = 1630976400  # start timestamp the MSFT test data uses

    # ================================= Act ====================================
    result = test_object.get_bars_data('MSFT', unix_past, unix_now)

    # ================================= Assert =================================
    assert len(result.columns) == 6
    assert len(result['Close']) == 537


@patch('requests.get')
def test_get_bars_data_connection_error(mocker):
    """Test get_bars_data to ensure function throws correct error."""
    # ================================= Arrange ================================
    # Note: this is the 1-stop-shop way of doing it - this DOES NOT require a fixture
    # mocker is the patched requests.get defined in the decorator
    # when we call requests.get(), produce a side effect of connection error
    mocker.side_effect = requests.exceptions.ConnectionError()

    # calculate window times (as it is in auto_trader)
    unix_now = int(time.time())
    unix_past = unix_now - 63072000  # 2 years

    # ================================= Act ====================================

    # ================================= Assert =================================
    try:
        test_object.get_bars_data('MSFT', unix_past, unix_now)
        assert False
    except requests.exceptions.ConnectionError:
        assert True


@patch('requests.get')
def test_get_data_non_200(mocker):
    """Test get_bars_data to ensure function throws correct error."""
    # ================================= Arrange ================================
    # for some reason, this 1-stop-shop way of doing it is the only way that works
    # for setting up the status code to correctly return the status code defined in
    # the response object
    mocker.return_value = mocker
    mocker.return_value.status_code = api_400_response.status_code

    # unix dates don't matter because the data is mocked, but we do this to simulate
    # actual unix values used as parameters
    unix_now = int(time.time())
    unix_past = unix_now - 63072000  # 2 years

    # ================================= Act ====================================

    # ================================= Assert =================================
    try:
        test_object.get_bars_data('MSFT', unix_past, unix_now)
        assert False
    except InvalidSymbolError:
        assert True


@patch('requests.get')
def test_get_data_empty_return_data(mocker):
    """Test get_bars_data to ensure function throws correct error."""
    # ================================= Arrange ================================
    # for some reason, this 1-stop-shop way of doing it is the only way that works
    # for setting up the status code to correctly return the status code defined in
    # the response object
    mocker.return_value = mocker
    mocker.return_value.status_code = api_200_EMPTY_response.status_code
    mocker.json.return_value = api_200_EMPTY_response.json()

    # unix dates don't matter because the data is mocked, but we do this to simulate
    # actual unix values used as parameters
    unix_now = int(time.time())
    unix_past = unix_now - 63072000  # 2 years

    # ================================= Act ====================================

    # ================================= Assert =================================
    try:
        test_object.get_bars_data('MSFT', unix_past, unix_now)
        assert False
    except InvalidSymbolError:
        assert True
