# StockBench
A back-tester for testing stock trading strategies with historical data.

![chart](https://github.com/jocon15/StockBench/blob/master/images/example_chart.png)

## Getting Started
1. First, you need to get your own API keys from [Aplaca Markets](https://alpaca.markets/).

2. Add them as [Environment Variables](https://github.com/jocon15/StockBench/wiki/Environment-Variables).

3. Before building a strategy, check out [Building a Strategy](https://github.com/jocon15/StockBench/wiki/Building-a-Strategy).

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
This project is currently in-development. The intention of this project is to be a proof-of-concept for simulating stock trading strategies. So far, we have had success in simulating strategies with multiple basic triggers.

As seen from the charts, a ellegant chart can be produced depiting the simulation results. The logging is working as intended and the production of an excel sheet with the simulation data is under develoment.

I will likely be making changes to several things, listed below.

#### Recently Built Features
- [x] Support of AND and OR triggers (complex triggering)
- [x] Support for variable triggers (complex triggering)
- [x] Support for volume triggers
- [x] Support for volume charting
- [x] Support for exporting simulation data to excel

#### Low Level Development
- [ ] Logging for the export API
- [ ] Volume bar is overly dark
- [ ] Update images in the readme
- [ ] Add images of the indicators to the wiki
- [ ] Sub chart titles (side)
- [ ] General cleanup and optimization (in-progress)

#### Upcoming Features
- [ ] Provide support for additional indicators.
- [ ] Investigate posible GUI interface
- [ ] Investigate news search triggering with Google search date filters
