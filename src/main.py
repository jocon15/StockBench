import time
from StockBench.simulator import Simulator

strategy = {
    'start': int(time.time()) - 8640000,  # 100 days in the past
    'end': int(time.time()),              # now
    'buy': {
        'RSI': '<40',
        'SMA20': '>256',
        'price': '>200',
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
    stock_sim = Simulator(1000.0)

    stock_sim.load_strategy(strategy)

    stock_sim.run('MSFT')


if __name__ == '__main__':
    main()
