import os
import time
import logging
import requests
from pandas import DataFrame
from datetime import datetime
from StockBench.constants import DELAY_SECONDS_15MIN
from StockBench.function_tools.function_wrappers import performance_timer

log = logging.getLogger()


class InvalidSymbolError(Exception):
    """Custom exception for when an unrecognized symbol is passed in."""
    pass


class Broker:
    """Interface for broker data."""
    _API_KEY = os.environ['ALPACA_API_KEY']
    _SECRET_KEY = os.environ['ALPACA_SECRET_KEY']

    _BARS_URL = 'https://data.alpaca.markets/v2/stocks/bars?'
    _HEADERS = {'APCA-API-KEY-ID': _API_KEY, 'APCA-API-SECRET-KEY': _SECRET_KEY}

    # alpaca defaults to 1,000 ohlc bars per request, but we can set it all the way to 10,000
    # this allows us to support 5 year simulation with a single request and not have to use the next page token
    _LIMIT = 10000

    # leeway for matching actual request dates with requested dates
    # takes into account that there may be weekends or holidays at the requested start date which means the broker
    # returns a slightly different date than requested
    _4_DAYS_IN_SECONDS_EPSILON = 345600

    def __init__(self, timeout=15):
        self.__timeout = timeout

    @performance_timer
    def get_daily_data(self, symbol: str, start_date_unix: int, end_date_unix: int):
        """Retrieve bars data with 1-Day resolution.

        Args:
            symbol: The asset symbol to retrieve data for.
            start_date_unix: The start date in unix.
            end_date_unix: The end date in unix.

        return:
            JSON: The request data.
        """
        log.debug('Building URI...')

        start_date_utc, end_date_utc = self.__unix_to_utc_date(start_date_unix, end_date_unix)
        start_time_utc, end_time_utc = self.__unix_to_utc_time(start_date_unix, end_date_unix)

        day_bars_url = f'{self._BARS_URL}' \
                       f'symbols={symbol}' \
                       f'&start={start_date_utc}' \
                       f'T{start_time_utc}Z' \
                       f'&end={end_date_utc}' \
                       f'T{end_time_utc}Z' \
                       f'&limit={self._LIMIT}' \
                       f'&timeframe=1D'
        log.debug(f'Completed URI: {day_bars_url}')
        return self.__make_request(day_bars_url, symbol, start_date_unix, end_date_unix)

    def __make_request(self, uri: str, symbol: str, start_date_unix: int, end_date_unix: int):
        """Make the Brokerage API request.

        Args:
            uri: The URI to use in the request.
            symbol: The symbol to use in the request.

        return:
            JSON: The request data (keyed with 'bars' and 'symbol').

        raises:
            ValueError: If the symbol passed is invalid.
        """
        log.debug('Attempting request...')
        try:
            response = requests.get(uri, headers=self._HEADERS, timeout=self.__timeout)
            if response.status_code != 200:
                log.critical('Request unsuccessful!')
            response_data = response.json()
            log.debug('Request made successfully')
            if 'bars' not in response_data.keys():
                # symbols with numeric characters are flagged by broker
                raise InvalidSymbolError(f'Invalid symbol {symbol}')
            if response_data['bars'] == {}:
                # misspelled symbols return blank data for bars
                raise InvalidSymbolError(f'Invalid symbol {symbol}')
            ohlc_data = response_data['bars'][symbol]
            self.__validate_ohlc_data(ohlc_data, start_date_unix, end_date_unix)
            return self.__json_to_df(ohlc_data)
        except requests.exceptions.ConnectionError:
            log.critical('Connection error during request')
            print('Connection error trying to connect to brokerage servers!')

    def __validate_ohlc_data(self, ohlc_data: list, start_date_unix: int, end_date_unix: int):
        """Validate that the broker returned the data range requested by matching timestamps with buffer applied."""
        timestamp_format = '%Y-%m-%dT%H:%M:%SZ'

        actual_start_timestamp = ohlc_data[0]['t']
        actual_end_timestamp = ohlc_data[-1]['t']

        actual_start_timestamp_datetime = datetime.strptime(actual_start_timestamp, timestamp_format)
        actual_end_timestamp_datetime = datetime.strptime(actual_end_timestamp, timestamp_format)

        actual_start_timestamp_unix = int(time.mktime(actual_start_timestamp_datetime.timetuple()))
        actual_end_timestamp_unix = int(time.mktime(actual_end_timestamp_datetime.timetuple()))

        if abs(actual_start_timestamp_unix - start_date_unix) > self._4_DAYS_IN_SECONDS_EPSILON:
            raise ValueError('Broker returned start date does not match requested start date! This symbol may not have '
                             'enough data!')

        if abs(actual_end_timestamp_unix - end_date_unix) > self._4_DAYS_IN_SECONDS_EPSILON:
            raise ValueError('Broker returned end date does not match requested start date! This symbol may not have '
                             'enough data!')

    @staticmethod
    def get_hourly_data():
        return NotImplementedError('Hourly bar data is not supported yet.')

    @staticmethod
    def get_minute_data():
        return NotImplementedError('Minute bar data is not supported yet.')

    @staticmethod
    def __unix_to_utc_date(start_date_unix: int, end_date_unix: int) -> tuple:
        """Convert 2 dates from unix to UTC-date."""
        # Note: end_date_utc is - 16 minutes to adjust for 15 minute historical data delay
        return (datetime.fromtimestamp(start_date_unix).strftime('%Y-%m-%d'),
                datetime.fromtimestamp(end_date_unix - DELAY_SECONDS_15MIN).strftime('%Y-%m-%d'))

    @staticmethod
    def __unix_to_utc_time(start_date_unix: int, end_date_unix: int) -> tuple:
        """Convert 2 dates from unix to UTC-time."""
        # Note: end_date_utc is - 16 minutes to adjust for 15 minute historical data delay
        return (datetime.fromtimestamp(start_date_unix - DELAY_SECONDS_15MIN).strftime('%H:%M:%S'),
                datetime.fromtimestamp(end_date_unix - DELAY_SECONDS_15MIN).strftime('%H:%M:%S'))

    @staticmethod
    def __json_to_df(ohlc_data: list) -> DataFrame:
        """Convert JSON to Pandas.DataFrame.

        Args:
            ohlc_data : The JSON data to convert.

        return
            Pandas.DataFrame: The converted data as a DateFrame.
        """
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
