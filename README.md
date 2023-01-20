# StockBench
A back-tester for testing stock trading strategies with historical data.

![chart](https://github.com/jocon15/StockBench/blob/master/images/example_chart.png)

## Getting Started
First, you need to get your own API keys from [Aplaca Markets](https://alpaca.markets/).

Add them as [Environment Variables](https://github.com/jocon15/StockBench/wiki/Environment-Variables).

Check out [Building a Strategy](https://github.com/jocon15/StockBench/wiki/Building-a-Strategy) for more information about constructing a custom strategy.

Setup your simulation...
```
import time
from StockBench.simulator import Simulator
import StockBench.constants as const

strategy = {
    'start': int(time.time()) - const.SECONDS_5_YEAR,
    'end': int(time.time()),
    'buy': {
        'RSI': '<40',
        'SMA20': '>256',
    },
    'sell': {
        'stop_loss': '50',
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
![chart](https://github.com/jocon15/StockBench/blob/master/images/example_chart.png)


## Diving Deeper
StockBench allows users to generate a report of all the data used during the simulation. By enabling reporting, the simulation will generate an Excel file.

![report](https://github.com/jocon15/StockBench/blob/master/images/excel.png)

# Under Construction
This project is currently in-development. The intention of this project is to be a proof-of-concept for simulating stock trading strategies. So far, we have had success in simulating strategies with multiple basic triggers.

As seen from the charts, a ellegant chart can be produced depiting the simulation results. The logging is working as intended and the production of an excel sheet with the simulation data is under develoment.

I will likely be making changes to several things, listed below.

- [x] Provide support for variable triggers. EX: sell if SMA20 > current price (complex triggering)
- [ ] Provide support for additional indicators.
- [ ] Provide support for exporting simulation data to excel
- [ ] Investigate potential better ways for user to define strategy
- [ ] Investigate posible GUI interface
- [ ] Investigate news search triggering with Google search date filters
