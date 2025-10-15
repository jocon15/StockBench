import time
import logging
from functools import wraps
from typing import Callable
from datetime import datetime

import requests
from requests import Response
from pandas import DataFrame

from StockBench.controllers.simulator.broker.configuration import BrokerConfiguration

log = logging.getLogger()


class MissingCredentialError(Exception):
    """Custom exception for when a credential is missing."""
    pass


class InvalidSymbolError(Exception):
    """Custom exception for when an unrecognized symbol is passed in."""
    pass


class InsufficientDataError(Exception):
    """Custom exception for when a symbol has not been around long enough to provide the sufficient amount of data."""
    pass


def logged_request(original_fxn: Callable):
    """Decorator for logging outcomes of request functions."""
    @wraps(original_fxn)
    def wrapper(self, url, context):
        try:
            response = original_fxn(self, url, context)
        except requests.exceptions.ConnectionError:
            log.exception(f'Connection error in {context}!')
            raise requests.exceptions.ConnectionError(f'Connection error in {context}!')

        if not BrokerClient.is_response_success(response.status_code):
            log.exception(f'API returned: {response.status_code} on {context} PATCH request!')

        return response
    return wrapper


class BrokerClient:
    """Encapsulates a broker client."""
    _BARS_URL = 'https://data.alpaca.markets/v2/stocks/bars?'

    _TIMEOUT = 10

    # alpaca defaults to 1,000 ohlc bars per request, but we can set it all the way to 10,000
    # this allows us to support 5 year simulation with a single request and not have to use the next page token
    _LIMIT = 10000

    # leeway for matching actual request dates with requested dates
    # takes into account that there may be weekends or holidays at the requested start date which means the broker
    # returns a slightly different date than requested
    _4_DAYS_IN_SECONDS_EPSILON = 345600

    def __init__(self, config: BrokerConfiguration):
        self.__validate_config(config)
        self.__headers = {'APCA-API-KEY-ID': config.public_key, 'APCA-API-SECRET-KEY': config.private_key}
        self.__additional_payload = None

    def get_bars_data(self, symbol: str, start_date_unix: int, end_date_unix: int) -> DataFrame:
        """Get bars data with 1-Day resolution.

        Note: If you run this in a container like docker, the time stamp time.time() will return a UTC timestamp, not
        a timestamp in local time. Because the NYSE operates on eastern time, the timestamp will be wrong, causing
        a 403 response because data was requested for a time in the future. The end date is maintained here to allow
        users to still retain control the end date.
        """
        day_bars_url = f'{self._BARS_URL}' \
                       f'symbols={symbol}' \
                       f'&start={self.unix_to_utc_date(start_date_unix)}' \
                       f'T{self.unix_to_utc_time(start_date_unix)}Z' \
                       f'&end={self.unix_to_utc_date(end_date_unix)}' \
                       f'T{self.unix_to_utc_time(end_date_unix)}Z' \
                       f'&limit={self._LIMIT}' \
                       f'&timeframe=1D'

        time.sleep(0.1)  # rate limit buffer

        response = self.__send_GET_request(day_bars_url, 'get_data')
        validated_data = self.__validate_ohlc_data(symbol, response.json(), start_date_unix, end_date_unix)
        return self.__json_to_df(validated_data)

    def __validate_ohlc_data(self, symbol: str, response_data: dict, start_date_unix: int, end_date_unix: int) -> list:
        """Validate that the broker returned the data range requested by matching timestamps with buffer applied."""
        timestamp_format = '%Y-%m-%dT%H:%M:%SZ'

        if 'bars' not in response_data.keys():
            # symbols with numeric characters are flagged by broker
            raise InvalidSymbolError(f'Invalid symbol {symbol}')
        if response_data['bars'] == {}:
            # misspelled symbols return blank data for bars
            raise InvalidSymbolError(f'Invalid symbol {symbol}')

        ohlc_data = response_data['bars'][symbol]

        actual_start_timestamp = ohlc_data[0]['t']
        actual_end_timestamp = ohlc_data[-1]['t']

        actual_start_timestamp_datetime = datetime.strptime(actual_start_timestamp, timestamp_format)
        actual_end_timestamp_datetime = datetime.strptime(actual_end_timestamp, timestamp_format)

        actual_start_timestamp_unix = int(time.mktime(actual_start_timestamp_datetime.timetuple()))
        actual_end_timestamp_unix = int(time.mktime(actual_end_timestamp_datetime.timetuple()))

        if abs(actual_start_timestamp_unix - start_date_unix) > self._4_DAYS_IN_SECONDS_EPSILON:
            raise InsufficientDataError(f'Broker returned start date does not match requested start date! {symbol} may '
                                        f'not have enough data!')

        if abs(actual_end_timestamp_unix - end_date_unix) > self._4_DAYS_IN_SECONDS_EPSILON:
            raise InsufficientDataError('Broker returned end date does not match requested start date! {symbol} may '
                                        'not have enough data!')

        return ohlc_data

    @staticmethod
    def __validate_config(config: BrokerConfiguration):
        if not config.public_key:
            raise MissingCredentialError('Could not find public key environment variable!')
        if not config.private_key:
            raise MissingCredentialError('Could not find private key environment variable!')

    @staticmethod
    def __unix_to_utc_date(start_date_unix: int, end_date_unix: int) -> tuple:
        """Convert 2 dates from unix to UTC-date."""
        # Note: end_date_utc is - 16 minutes to adjust for 15 minute historical data delay
        return (datetime.fromtimestamp(start_date_unix).strftime('%Y-%m-%d'),
                datetime.fromtimestamp(end_date_unix).strftime('%Y-%m-%d'))

    @staticmethod
    def __unix_to_utc_time(start_date_unix: int, end_date_unix: int) -> tuple:
        """Convert 2 dates from unix to UTC-time."""
        # Note: end_date_utc is - 16 minutes to adjust for 15 minute historical data delay
        return (datetime.fromtimestamp(start_date_unix).strftime('%H:%M:%S'),
                datetime.fromtimestamp(end_date_unix).strftime('%H:%M:%S'))

    @staticmethod
    def __json_to_df(ohlc_data: list) -> DataFrame:
        """Convert OHLC data list to dataframe."""
        log.debug('Converting JSON data to DataFrame...')

        time_values = [str(data_point['t']) for data_point in ohlc_data]
        open_values = [float(data_point['o']) for data_point in ohlc_data]
        high_values = [float(data_point['h']) for data_point in ohlc_data]
        low_values = [float(data_point['l']) for data_point in ohlc_data]
        close_values = [float(data_point['c']) for data_point in ohlc_data]
        volume_values = [float(data_point['v']) for data_point in ohlc_data]

        df = DataFrame()
        df.insert(0, 'Date', time_values)  # noqa
        df.insert(1, 'Open', open_values)  # noqa
        df.insert(2, 'High', high_values)  # noqa
        df.insert(3, 'Low', low_values)  # noqa
        df.insert(4, 'Close', close_values)  # noqa
        df.insert(5, 'volume', volume_values)  # noqa

        log.debug('Conversion complete')
        return df

    @logged_request
    def __send_GET_request(self, url: str, context: str) -> Response:
        """Send a GET request. (context used by decorator)"""
        return requests.get(url, headers=self.__headers, timeout=self._TIMEOUT)

    @logged_request
    def __send_POST_request(self, url: str, context: str) -> Response:
        """Send a POST request. (context used by decorator)"""
        return requests.post(url, headers=self.__headers, json=self.__additional_payload, timeout=self._TIMEOUT)

    @logged_request
    def __send_PATCH_request(self, url: str, context: str) -> Response:
        """Send a PATCH request. (context used by decorator)"""
        return requests.patch(url, headers=self.__headers, json=self.__additional_payload, timeout=self._TIMEOUT)

    @logged_request
    def __send_DELETE_request(self, url: str, context: str) -> Response:
        """Send a DELETE request. (context used by decorator)"""
        return requests.delete(url, headers=self.__headers, timeout=self._TIMEOUT)

    @staticmethod
    def unix_to_utc_date(date_unix: int) -> str:
        """Convert date from unix to UTC-date."""
        return datetime.fromtimestamp(date_unix).strftime('%Y-%m-%d')

    @staticmethod
    def unix_to_utc_time(date_unix: int) -> str:
        """Convert date from unix to UTC-time."""
        return datetime.fromtimestamp(date_unix).strftime('%H:%M:%S')

    @staticmethod
    def is_response_success(status_code: int) -> bool:
        return True if 200 <= status_code <= 299 else False
