import os
import logging
import requests
import pandas as pd
from datetime import datetime
from StockBench.constants import DELAY_SECONDS_15MIN
from StockBench.function_tools.function_wrappers import performance_timer

log = logging.getLogger()


class Broker:
    """Interface for broker data."""
    _API_KEY = os.environ['ALPACA_API_KEY']
    _SECRET_KEY = os.environ['ALPACA_SECRET_KEY']

    _BARS_URL = 'https://data.alpaca.markets/v2/stocks/bars?'
    _HEADERS = {'APCA-API-KEY-ID': _API_KEY, 'APCA-API-SECRET-KEY': _SECRET_KEY}

    def __init__(self, timeout=15):
        """Constructor.

        Args:
            timeout: Timeout length (seconds).
        """
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
        # convert dates from unix to utc
        start_date_utc, end_date_utc = self.__unix_to_utc_date(start_date_unix, end_date_unix)
        # convert times from unix to utc
        start_time_utc, end_time_utc = self.__unix_to_utc_time(start_date_unix, end_date_unix)

        day_bars_url = f'{self._BARS_URL}' \
                       f'symbols={symbol}' \
                       f'&start={start_date_utc}' \
                       f'T{start_time_utc}Z' \
                       f'&end={end_date_utc}' \
                       f'T{end_time_utc}Z' \
                       f'&timeframe=1D'
        log.debug(f'Completed URI: {day_bars_url}')
        return self.__make_request(day_bars_url, symbol)

    def __make_request(self, uri: str, symbol: str):
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
                # symbols with numeric characters are flagged by the broker
                raise ValueError(f'Invalid symbol {symbol}')
            if response_data['bars'] == {}:
                # misspelled symbols return blank data for bars
                raise ValueError(f'Invalid symbol {symbol}')
            return self.__json_to_df(response_data['bars'][symbol])
        except requests.exceptions.ConnectionError:
            # do something if the request fails
            log.critical('Connection error during request')
            print('Connection error trying to connect to brokerage servers!')

    @staticmethod
    def get_hourly_data():
        return NotImplementedError('Hourly bar data is not supported yet.')

    @staticmethod
    def get_minute_data():
        return NotImplementedError('Minute bar data is not supported yet.')

    @staticmethod
    def __unix_to_utc_date(start_date_unix: int, end_date_unix: int) -> tuple:
        """Convert 2 dates from unix to UTC-date.

        Args:
            start_date_unix: Start date in unix.
            end_date_unix: End date in unix.

        return:
            tuple: The converted dates in UTC-date format.

        """
        # Note: end_date_utc is - 16 minutes to adjust for 15 minute historical data delay
        return (datetime.fromtimestamp(start_date_unix).strftime('%Y-%m-%d'),
                datetime.fromtimestamp(end_date_unix - DELAY_SECONDS_15MIN).strftime('%Y-%m-%d'))

    @staticmethod
    def __unix_to_utc_time(start_date_unix: int, end_date_unix: int) -> tuple:
        """Convert 2 dates from unix to UTC-time.

        Args:
            start_date_unix: Start date in unix.
            end_date_unix: End date in unix.

        return:
            tuple: The converted dates in UTC-time format.
        """
        # Note: end_date_utc is - 16 minutes to adjust for 15 minute historical data delay
        return (datetime.fromtimestamp(start_date_unix - DELAY_SECONDS_15MIN).strftime('%H:%M:%S'),
                datetime.fromtimestamp(end_date_unix - DELAY_SECONDS_15MIN).strftime('%H:%M:%S'))

    @staticmethod
    def __json_to_df(json_data):
        """Convert JSON to Pandas.DataFrame.

        Args:
            json_data (JSON): The JSON data to convert.

        return
            Pandas.DataFrame: The converted data as a DateFrame.

        raises
            ValueError: If the symbol does not have sufficient data.
        """
        log.debug('Converting JSON to DF...')
        time_values = []
        open_values = []
        high_values = []
        low_values = []
        close_values = []
        volume_values = []
        for data_point in json_data:
            # check for duplicated data (implies this symbol has not been around long enough)
            # Alpaca records all points as the same value if this happens
            if data_point['h'] == data_point['c'] and data_point['l'] == data_point['c']:
                raise ValueError('This symbol does not have enough data!')

            time_values.append(str(data_point['t']))
            open_values.append(float(data_point['o']))
            high_values.append(float(data_point['h']))
            low_values.append(float(data_point['l']))
            close_values.append(float(data_point['c']))

            volume_values.append(float(data_point['v']))
        df = pd.DataFrame()
        df.insert(0, 'Date', time_values)  # noqa
        df.insert(1, 'Open', open_values)  # noqa
        df.insert(2, 'High', high_values)  # noqa
        df.insert(3, 'Low', low_values)  # noqa
        df.insert(4, 'Close', close_values)  # noqa
        df.insert(5, 'volume', volume_values)  # noqa
        log.debug('Conversion complete')
        return df
