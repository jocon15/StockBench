import traceback
from functools import wraps
from typing import Callable

import requests

from StockBench.controllers.simulator.algorithm.exceptions import MalformedStrategyError
from StockBench.controllers.simulator.broker.broker_client import MissingCredentialError, InvalidSymbolError, \
    InsufficientDataError
from StockBench.controllers.simulator.indicator.exceptions import StrategyIndicatorError
from StockBench.controllers.simulator.simulator import Simulator
from StockBench.models.observers.progress_observer import ProgressObserver


def SimulationProxyFunction(simulation_fxn: Callable):
    """Decorator for a simulation proxy function. Wraps the simulation in a try block and catches any errors."""

    def wrapper(*args, **kwargs):
        try:
            return simulation_fxn(*args, **kwargs)
        except requests.exceptions.ConnectionError:
            message = 'Failed to connect to broker!'
        except MalformedStrategyError as e:
            message = f'Malformed strategy error: {e}'
        except StrategyIndicatorError as e:
            message = f'Strategy error: {e}'
        except MissingCredentialError as e:
            message = f'Missing credential error: {e}'
        except InvalidSymbolError as e:
            message = f'Invalid symbol error: {e}'
        except InsufficientDataError as e:
            message = f'Insufficient data error {e}'
        except Exception as e:
            message = f'Unexpected error: {type(e)} {e} {traceback.print_exc()}'

        return {'status_code': 400, 'message': message}

    return wrapper


class SimulationProxy:
    """Proxy function acting as a middle man between the controller and the simulator. Allows us to wrap the proxy
    function to handle errors that the simulator throws."""
    @staticmethod
    @SimulationProxyFunction
    def run_singular_simulation(strategy: dict, symbol: str, initial_balance: float, logging_on: bool, reporting_on: bool,
                                progress_observer: ProgressObserver) -> dict:
        simulator = Simulator(initial_balance)

        simulator.load_strategy(strategy)

        if logging_on:
            simulator.enable_logging()
        if reporting_on:
            simulator.enable_reporting()

        return simulator.run(symbol, progress_observer)
