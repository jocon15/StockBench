# StockBench
A back-tester for testing stock trading strategies on historical data.

![chart](https://github.com/jocon15/StockBench/blob/master/images/example_chart.png)

## Getting Started
First, you need to get your own API keys from https://alpaca.markets/.

Add them as environment variables.

Setup your simulation...
```
import time
from StockBench.simulator import Simulator
import StockBench.constants as const

strategy = {
    'start': int(time.time()) - const.SECONDS_5_YEAR,  # 100 days in the past
    'end': int(time.time()),                           # now
    'buy': {
        'RSI': '<40',
        'SMA20': '>256',
        }
    },
    'sell': {
        'stop_loss': '50',
    }
}

# simulation settings
stock_sim = Simulator(1000.00)
stock_sim.enable_logging()
stock_sim.enable_developer_logging()
stock_sim.load_strategy(strategy)
stock_sim.enable_reporting()
stock_sim.enable_charting()

# run the simulation on MSFT
stock_sim.run('MSFT')

```

## Results
![chart](https://github.com/jocon15/StockBench/blob/master/images/example_chart.png)

# Under Construction
This project is currently under development. The intention of this project is to be a proof-of-concept for simulating stock trading strategies. So far, we have had success in simulating strategies with multiple basic triggers.

As seen from the charts, a ellegant chart can be produced depiting the simulation results. The logging is working as intended and the production of an excel sheet with the simulation data is under develoment.

I will likely be making changes to several things, listed below.

- [ ] Provide support for 'and' triggers. EX: sell if RSI > 60 and SMA20 > 26 (complex triggering)
- [ ] Provide support for variable triggers. EX: sell if SMA20 > current price (complex triggering)
- [ ] Provide support for additional indicators.
- [ ] Provide support for exporting simulation data to excel
- [ ] Investigate potential better ways for user to define strategy
- [ ] Posible GUI interface
