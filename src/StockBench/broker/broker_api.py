import os
import json
import requests
import pandas as pd
from datetime import datetime


class BrokerAPI:
    def __init__(self, timeout=5):
        self.__API_KEY = os.environ['ALPACA_API_KEY']
        self.__SECRET_KEY = os.environ['ALPACA_SECRET_KEY']

        self.__BASE_URL = 'https://api.alpaca.markets'
        self.__BARS_URL = 'https://data.alpaca.markets/v2/stocks/bars?'
        self.__ACCOUNT_URL = '{}/v2/account'.format(self.__BASE_URL)
        self.__POSITIONS_URL = '{}/v2/positions/'.format(self.__BASE_URL)
        self.__CLOSE_URL = '{}/v2/positions/'.format(self.__BASE_URL)
        self.__ORDERS_URL = '{}/v2/orders'.format(self.__BASE_URL)
        self.__CLOCK_URL = '{}/v2/clock'.format(self.__BASE_URL)
        self.__ASSET_URL = '{}/v2/assets/'.format(self.__BASE_URL)
        self.__UPDATE_CONFIGURATIONS_URL = '{}/v2/account/configurations'.format(self.__BASE_URL)
        self.__HEADERS = {'APCA-API-KEY-ID': self.__API_KEY, 'APCA-API-SECRET-KEY': self.__SECRET_KEY}
        self.__timeout = timeout

        self.__symbol = None

    def get_daily_data(self, symbol: str, start_date_unix: int, end_date_unix: int):
        self.__symbol = symbol
        # convert dates from unix to utc
        start_date_utc, end_date_utc = self.__unix_to_utc_date(start_date_unix, end_date_unix)
        # convert times from unix to utc
        start_time_utc, end_time_utc = self.__unix_to_utc_time(start_date_unix, end_date_unix)

        day_bars_url = f'{self.__BARS_URL}' \
                       f'symbols={symbol}' \
                       f'&start={start_date_utc}' \
                       f'T{start_time_utc}Z' \
                       f'&end={end_date_utc}' \
                       f'T{end_time_utc}Z' \
                       f'&timeframe=24Hour'

        return self.__make_request(day_bars_url)

    def get_hourly_data(self):
        pass

    def get_minute_data(self):
        pass

    @staticmethod
    def __unix_to_utc_date(start_date_unix: int, end_date_unix: int):
        # Note: end_date_utc is - 16 minutes to adjust for 15 minute historical data delay
        return (datetime.utcfromtimestamp(start_date_unix).strftime('%Y-%m-%d'),
                datetime.utcfromtimestamp(end_date_unix - 960).strftime('%Y-%m-%d'))

    @staticmethod
    def __unix_to_utc_time(start_date_unix, end_date_unix):
        # Note: end_date_utc is - 16 minutes to adjust for 15 minute historical data delay
        return (datetime.utcfromtimestamp(start_date_unix - 960).strftime('%H:%M:%S'),
                datetime.utcfromtimestamp(end_date_unix - 960).strftime('%H:%M:%S'))

    def __make_request(self, uri: str):
        try:
            response = requests.get(uri, headers=self.__HEADERS, timeout=self.__timeout).json()
            return self.json_to_df(response['bars'][self.__symbol])
        except requests.exceptions.ConnectionError:
            # do something if the request fails
            pass

    @staticmethod
    def json_to_df(json_data):
        t = []
        o = []
        h = []
        l = []
        c = []
        for data_point in json_data:
            t.append(str(data_point['t']))
            o.append(float(data_point['o']))
            h.append(float(data_point['h']))
            l.append(float(data_point['l']))
            c.append(float(data_point['c']))
        df = pd.DataFrame()
        df.insert(0, 'Date', t)
        df.insert(1, 'Open', o)
        df.insert(2, 'High', h)
        df.insert(3, 'Low', l)
        df.insert(4, 'Close', c)
        return df


if __name__ == '__main__':
    import time
    sym = 'MSFT'
    end = int(time.time())
    start = end - 8640000

    api = BrokerAPI()

    data = api.get_daily_data(sym, start, end)

    # print(json.dumps(data, indent=4))
    print(len(data))

    # there are weekends and holidays where there is no data available
    # so even if we - 100 days in seconds from the now timestamp,
    # there's only 76 data points, not 100, so that distinction needs to
    # be known by the user

    # The data is CORRECT, but it might not be intuitive to the user right away

