<p align="center">
    <img src ="https://img.shields.io/badge/version-1.16.0-blueviolet.svg"/> <img src ="https://img.shields.io/badge/platform-windows-yellow.svg"/> <img src ="https://img.shields.io/badge/python-^3-blue.svg" /> <img src ="https://img.shields.io/github/license/jocon15/StockBench.svg?color=orange"/>
</p>

# StockBench

### A back-testing app for testing stock trading strategies with historical data.

<p align="center">
    <img src="https://github.com/jocon15/StockBench/blob/master/images/singular_v2.gif" />
</p>

# How it Works

StockBench is a stock simulation suite designed for testing strategies on historical data. StockBench sources market data from [Alpaca Markets](https://alpaca.markets/). You will need an Alpaca account to use this app.

StockBench is designed to test strategies that use technical analysis. StockBench allows for quite some freedom in defining a strategy. It can be simple or complex. Once you have a strategy picked out, you can play with the simulation settings. Check out the [StockBench Wiki](https://github.com/jocon15/StockBench/wiki) for more information on settings, indicators, and rules.

Now that you have everything the way you like, you can start the simulation. The simulator will request the data relevant to your strategy. As expected, the simulator iterates over the data as if it were trading in real time. The simulator is allowed to access previous data, but never future data. The simulator makes artificial trades based on your strategy. Once the simulation is complete, the terminal will show the results of the simulation. A chart will then pop up showing the price data and any other indicators defined in the strategy.

And just like that, you have simulated a strategy on historical data. Have fun!

| Configuration                                                                         | Results                                                                        |
|:-------------------------------------------------------------------------------------:|:------------------------------------------------------------------------------:|
| ![single](https://github.com/jocon15/StockBench/blob/master/images/configuration.png) | ![multi](https://github.com/jocon15/StockBench/blob/master/images/results.png) |

## In-Depth Results Across Multiple Strategies

Powerful interactive analytics allow you to compare multiple strategies at once.

<p align="center">
    <img src="https://github.com/jocon15/StockBench/blob/master/images/histogram.png" />
</p>

## Getting Started

1. First, you need to get your own API keys from [Alpaca Markets](https://alpaca.markets/).

2. Add them as [Environment Variables](https://github.com/jocon15/StockBench/wiki/Environment-Variables).

3. Restart your PC to enable the [Environment Variables](https://github.com/jocon15/StockBench/wiki/Environment-Variables).

4. Build your strategy JSON file. See [Building a Strategy](https://github.com/jocon15/StockBench/wiki/Building-a-Strategy) or try our new [Strategy Studio](#Strategy-Studio).

5. Run the StockBench.exe file.

6. Set your simulation parameters.

7. Run the simulation and view the results.

## Strategy Studio

Strategy Studio allows you to create and update strategy .json files. You can edit existing files or create new ones from a provided basic template.

<p align="center">
    <img src="https://github.com/jocon15/StockBench/blob/master/images/strategy_studio.gif" />
</p>

## Additional Results Analytics

Simulation results are split up into different tabs within the results window, giving you an in-depth look at how your strategy performed.

<p align="center">
    <img src="https://github.com/jocon15/StockBench/blob/master/images/additional_analytics.gif" />
</p>

## Head to Head

Want to run 2 strategies side by side? We have you covered with the compare tab!

<p align="center">
    <img src="https://github.com/jocon15/StockBench/blob/master/images/compare.gif" />
</p>

## Exporting Results
StockBench offers a set of exporting tools that allow you to keep simulation results. Check out our export to markdown 
feature that allow you to export your results to a markdown file. Markdown is especially well-equipped for developing
elegant documents with its simple and powerful syntax. Our markdown exporter creates a template for a study document 
and inserts the results of the simulation for you, making it a breeze to create studies easily.
![report](https://github.com/jocon15/StockBench/blob/master/images/markdown_export.png)

## Diving Deeper

If you are curious to see the underlying data used by the simulation, you can choose to export the simulation data using the reporting option. When chosen, a report of all the data used during the simulation will be generated. The report will be an excel (.xlsx) file.
![report](https://github.com/jocon15/StockBench/blob/master/images/excel.png)

# Roadmap

Check out our [Trello Board](https://trello.com/b/XtEbMZL4/stockbench) for more information on where we're headed next.
