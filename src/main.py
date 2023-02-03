import time
from StockBench.constants import *
from StockBench.simulator import Simulator


strategy = {
    'start': int(time.time()) - SECONDS_5_YEAR,
    'end': int(time.time()),
    'buy': {
        'RSI': '<30',
        'and1': {
            'SMA20': '>50',
            'color': {
                '1': 'red',
                '0': 'green'
            }
        },
        'price': '>200',
        'color': {
            '2': 'red',
            '1': 'red',
            '0': 'green'
        }
    },
    'sell': {
        'price': '<200',
        'RSI': '>60'
    }
}


def main():
    stock_sim = Simulator(1000.00)

    stock_sim.enable_logging()
    # stock_sim.enable_developer_logging(1)

    stock_sim.enable_reporting()
    stock_sim.enable_charting()

    stock_sim.load_strategy(strategy)

    # stock_sim.run('AAPL')

    print(stock_sim.run_multiple(['AAPL', 'MSFT', 'TSLA']))


if __name__ == '__main__':
    main()
