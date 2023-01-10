import time
from StockBench.simulator import Simulator
import StockBench.constants as const

strategy = {
    'start': int(time.time()) - const.SECONDS_5_YEAR,  # 100 days in the past
    'end': int(time.time()),                     # now
    'buy': {
        'RSI': '<40',
        'and1': {
            'SMA20': '>256',
            'RSI': '>10'
        },
        'price': '>200',  # FIXME: still need to implement this one
        'color': {
            '2': 'red',
            '1': 'red',
            '0': 'green'
        }
    },
    'sell': {
        'stop_loss': '50',
        'RSI': '>60'
    }
}


def main():
    stock_sim = Simulator(1000.00)

    stock_sim.enable_logging()
    stock_sim.enable_developer_logging()

    stock_sim.load_strategy(strategy)

    # stock_sim.enable_reporting()
    stock_sim.enable_charting()

    stock_sim.run('MSFT')


if __name__ == '__main__':
    main()
