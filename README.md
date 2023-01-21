# StockBench
#### A back-tester for testing stock trading strategies with historical data.

![chart](https://github.com/jocon15/StockBench/blob/master/images/example_chart.png)

# How it Works
StockBench allows you to run a simulation on any US security where data is available. StockBench sources market data from [Alpaca Markets](https://alpaca.markets/).

You begin by defining a strategy that you would like to test. StockBench allows for quite some freedom in defining a strategy. It can be simple or complex. Once you have a strategy picked out, you can play with the simulation settings. Check out the [StockBench Wiki](https://github.com/jocon15/StockBench/wiki) for more information on settings, indicators, and rules.

Now that you have everything the way you like, you can start the simulation. As expected, the simulator iterates over the data as if it were trading in real time. The simulator is allowed to access previous data, but never future data. It cannot see the future, yet. The simulator makes artificial trades based on your strategy. Once the simulation is complete, the terminal will show the results of the simulation. A chart will then pop up showing the price data and any other indicators defined in the strategy.

And just like that, you have simulated a strategy on historical data. Have fun!

## Getting Started
1. First, you need to get your own API keys from [Alpaca Markets](https://alpaca.markets/).

2. Add them as [Environment Variables](https://github.com/jocon15/StockBench/wiki/Environment-Variables).

3. Import the simulator and constants.

4. Build a strategy, check out [Building a Strategy](https://github.com/jocon15/StockBench/wiki/Building-a-Strategy).

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

# simulation settings
stock_sim = Simulator(1000.00)
stock_sim.enable_logging()
stock_sim.load_strategy(strategy)
stock_sim.enable_reporting()
stock_sim.enable_charting()

# run the simulation on MSFT
stock_sim.run('MSFT')

```

## Results
Each simulation will render a chart that shows the price data and relevant indicators.
![chart](https://github.com/jocon15/StockBench/blob/master/images/example_chart.png)


## Diving Deeper
StockBench allows users to generate a report of all the data used during the simulation. By enabling reporting, the simulation will generate an Excel file.

![report](https://github.com/jocon15/StockBench/blob/master/images/excel.png)

# Roadmap
This project is currently under development. The intention of this project is to be a proof-of-concept for simulating stock trading strategies on a large scale. We've shown that the dictionary strategy definition can be used as a means of defining a strategy with both basic and complex rules. Below we've listed some of the new features as well as things we'd like to see implemented or changed.


#### Recently Built Features
- [x] Support of AND and OR triggers (complex triggering)
- [x] Support for variable triggers (complex triggering)
- [x] Support for volume triggers
- [x] Support for volume charting
- [x] Support for terminal logging
- [x] Support for exporting simulation data to excel

#### Low Level Development
- [ ] Logging for the export API
- [ ] Volume bars are overly dark
- [ ] Update images in the readme
- [ ] Add images of the indicators to the wiki
- [ ] Sub chart titles (side)
- [ ] General cleanup and optimization (in-progress)

#### High Level Features
- [ ] Provide support for additional indicators.
- [ ] Investigate possible GUI
- [ ] Investigate news search triggering with Google search date filters
- [ ] Have the run function return the simulation results so the user can easily use them
