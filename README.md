# StockBench

<p align="center">
    <img src ="https://img.shields.io/badge/version-1.5.0-blueviolet.svg"/> <img src ="https://img.shields.io/badge/platform-windows-yellow.svg"/> <img src ="https://img.shields.io/badge/python-^3-blue.svg" /> <img src ="https://img.shields.io/github/license/jocon15/StockBench.svg?color=orange"/>
</p>

### A back-testing app for testing stock trading strategies with historical data.

![multi](https://github.com/jocon15/StockBench/blob/master/images/singular_v2.gif)

# How it Works

StockBench is a US security simulation suite designed for testing strategies on historical data. StockBench sources market data from [Alpaca Markets](https://alpaca.markets/).

Begin by defining a strategy that you would like to test. StockBench allows for quite some freedom in defining a strategy. It can be simple or complex. Once you have a strategy picked out, you can play with the simulation settings. Check out the [StockBench Wiki](https://github.com/jocon15/StockBench/wiki) for more information on settings, indicators, and rules.

Now that you have everything the way you like, you can start the simulation. The simulator will request the data relevant to your strategy. As expected, the simulator iterates over the data as if it were trading in real time. The simulator is allowed to access previous data, but never future data. The simulator makes artificial trades based on your strategy. Once the simulation is complete, the terminal will show the results of the simulation. A chart will then pop up showing the price data and any other indicators defined in the strategy.

And just like that, you have simulated a strategy on historical data. Have fun!

## Getting Started

1. First, you need to get your own API keys from [Alpaca Markets](https://alpaca.markets/).

2. Add them as [Environment Variables](https://github.com/jocon15/StockBench/wiki/Environment-Variables).

3. Restart your PC to enable the [Environment Variables](https://github.com/jocon15/StockBench/wiki/Environment-Variables).

4. Build your strategy .JSON file. See [Building a Strategy](https://github.com/jocon15/StockBench/wiki/Building-a-Strategy) or try our new [Strategy Studio (beta)](#Strategy-Studio).

5. Run the StockBench.exe.

6. Set your simuation parameters.

7. Run the simulation and view the results.

| Setup                                                                                        | Results                                                                               |
|:--------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------:|
| ![single](https://github.com/jocon15/StockBench/blob/master/images/configuration.png) | ![multi](https://github.com/jocon15/StockBench/blob/master/images/results.png) |

Or test your strategy on multiple symbols and see overview analytics:
![chart](https://github.com/jocon15/StockBench/blob/master/images/multi_display.png)

## Strategy Studio
![strategy studio](https://github.com/jocon15/StockBench/blob/master/images/strategy_studio.png)

Strategy Studio allows you to create and update strategy .json files. You can edit existing files or create new ones from a template.

## Additional Results Analytics
| Buy Rules Tab                                                     | Positions Tab                                                                              |
|:--------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------:|
| ![buy rules tab](https://github.com/jocon15/StockBench/blob/master/images/buy_rules_tab.png) | ![positions tab](https://github.com/jocon15/StockBench/blob/master/images/positions_tab.png) |

## Diving Deeper

StockBench allows users to generate a report of all the data used during the simulation. By enabling reporting, the simulation will generate an Excel (.xlsx) file.

![report](https://github.com/jocon15/StockBench/blob/master/images/excel.png)

# Roadmap

This project is currently under development. The intention of this project is to be a proof-of-concept for simulating stock trading strategies on a large scale. Check out our [Trello Board](https://trello.com/b/XtEbMZL4/stockbench) for more information on where we're headed next.
