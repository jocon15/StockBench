# StockBench
A back-tester for testing stock trading strategies on historical data

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
    'end': int(time.time()),                     # now
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

# rtun the simulation on MSFT
stock_sim.run('MSFT')

```

## Results
![chart](https://github.com/jocon15/StockBench/blob/master/images/example_chart.png)
