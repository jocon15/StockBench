import time
from StockBench.composites.snp500 import snp500_tickers
from StockBench.constants import *
from StockBench.simulator import Simulator

strategy = {
    'start': int(time.time()) - SECONDS_5_YEAR,
    'end': int(time.time()),
    'buy': {
        'EMA20': '<120'
    },
    'sell': {
        'EMA20': '>200'
    }
}


def main():
    stock_sim = Simulator(1000.00)

    # stock_sim.enable_logging()
    # stock_sim.enable_developer_logging(1)

    # stock_sim.enable_reporting()

    stock_sim.load_strategy(strategy)

    stock_sim.run('MSFT', show_chart=True, save_chart=False, dark_mode=True)

    # print(stock_sim.run_multiple(['AAPL', 'MSFT', 'TSLA']))

    # result = stock_sim.run_multiple(snp500_tickers[:20], show_individual_charts=False, save_individual_charts=False,
    #                                 show_chart=True, save_chart=False, dark_mode=True)

    # stock_sim.save_results('example_file_name')

    # stock_sim.display_results_from_save('example_file_name')

    # print(result)


if __name__ == '__main__':
    main()
