# StockBench
### A back-tester for testing stock trading strategies with historical data.

One Symbol                 |  Many Symbols
:-------------------------:|:-------------------------:
![single](https://github.com/jocon15/StockBench/blob/master/images/TSLA.png)  |  ![multi](https://github.com/jocon15/StockBench/blob/master/images/multi_display.png)



# How it Works
StockBench allows you to run a simulation on any US security where data is available. StockBench sources market data from [Alpaca Markets](https://alpaca.markets/).

You begin by defining a strategy that you would like to test. StockBench allows for quite some freedom in defining a strategy. It can be simple or complex. Once you have a strategy picked out, you can play with the simulation settings. Check out the [StockBench Wiki](https://github.com/jocon15/StockBench/wiki) for more information on settings, indicators, and rules.

Now that you have everything the way you like, you can start the simulation. The simulator will request the data relevant to your strategy. As expected, the simulator iterates over the data as if it were trading in real time. The simulator is allowed to access previous data, but never future data. The simulator makes artificial trades based on your strategy. Once the simulation is complete, the terminal will show the results of the simulation. A chart will then pop up showing the price data and any other indicators defined in the strategy.

And just like that, you have simulated a strategy on historical data. Have fun!

## Getting Started
1. First, you need to get your own API keys from [Alpaca Markets](https://alpaca.markets/).

2. Add them as [Environment Variables](https://github.com/jocon15/StockBench/wiki/Environment-Variables).

3. Run `pip install .` in the StockBench repository.

4. Import the simulator and constants in your script.

5. Build a strategy, check out [Building a Strategy](https://github.com/jocon15/StockBench/wiki/Building-a-Strategy).

```
import time
from StockBench.simulator import Simulator
import StockBench.constants as const

strategy = {
    'start': int(time.time()) - SECONDS_5_YEAR,
    'end': int(time.time()),
    'buy': {
        'RSI': '<30',
        'SMA20': '>50',
    },
    'sell': {
        'price': '<200',
        'RSI': '>60'
    }
}

stock_sim = Simulator(1000.00)
stock_sim.enable_logging()
stock_sim.load_strategy(strategy)
stock_sim.enable_reporting()
stock_sim.enable_charting()

stock_sim.run('MSFT')
```

## Results
Each simulation will render a chart that shows the price data and relevant indicators.
![chart](https://github.com/jocon15/StockBench/blob/master/images/MSFT.png)


## Diving Deeper
StockBench allows users to generate a report of all the data used during the simulation. By enabling reporting, the simulation will generate an Excel (.xlsx) file.

![report](https://github.com/jocon15/StockBench/blob/master/images/excel.png)

# Roadmap
This project is currently under development. The intention of this project is to be a proof-of-concept for simulating stock trading strategies on a large scale. Check out our [Trello Board](https://trello.com/b/XtEbMZL4/stockbench) for more information on where we're headed next.
