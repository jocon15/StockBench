import traceback
from functools import wraps
from typing import Callable, List

import requests

from StockBench.controllers.simulator.algorithm.exceptions import MalformedStrategyError
from StockBench.controllers.simulator.broker.broker_client import MissingCredentialError, InvalidSymbolError, \
    InsufficientDataError
from StockBench.controllers.simulator.indicator.exceptions import StrategyIndicatorError
from StockBench.controllers.simulator.simulator import Simulator
from StockBench.models.observers.progress_observer import ProgressObserver


def SimulatorProxyFunction(simulation_fxn: Callable):
    """Decorator for a simulation proxy function. Wraps the simulation in a try block and catches any errors."""
    @wraps(simulation_fxn)
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
            message = f'Insufficient data error: {e}'
        except Exception as e:
            message = f'Unexpected error: {type(e)} {e} {traceback.format_exc()}'

        return {'status_code': 400, 'message': message}

    return wrapper


class SimulatorProxy:
    """Proxy acting as a middle man between the controller and the simulator. Allows us to wrap the proxy function to
    handle errors that the simulator throws.

    NOTE: These functions must remain static unlike charting proxy because we want to use a new simulator instance for
    each proxy function call. We do not want a shared simulator instance because each result window using the controller
    (and therefore proxy) will use a different simulator instance that is configured the way the user wants it.
    """
    def __init__(self, simulator: Simulator):
        self.__simulator = simulator

    @SimulatorProxyFunction
    def run_singular_simulation(self, strategy: dict, symbol: str, initial_balance: float,
                                logging_on: bool, reporting_on: bool, progress_observer: ProgressObserver) -> dict:
        """Proxy function for running a singular symbol simulation with error capturing."""
        self.__simulator.set_initial_balance(initial_balance)
        self.__simulator.load_strategy(strategy)

        if logging_on:
            self.__simulator.enable_logging()
        if reporting_on:
            self.__simulator.enable_reporting()

        return self.__simulator.run(symbol, progress_observer)

    @SimulatorProxyFunction
    def run_multi_simulation(self, strategy: dict, symbols: List[str], initial_balance: float,
                             logging_on: bool, reporting_on: bool, progress_observer: ProgressObserver) -> dict:
        """Proxy function for running a multi-symbol simulation with error capturing."""
        self.__simulator.set_initial_balance(initial_balance)
        self.__simulator.load_strategy(strategy)

        if logging_on:
            self.__simulator.enable_logging()
        if reporting_on:
            self.__simulator.enable_reporting()

        return self.__simulator.run_multiple(symbols, progress_observer)

    @SimulatorProxyFunction
    def run_folder_simulation(self, strategies: List[dict], symbols: List[str], initial_balance: float,
                              logging_on: bool, reporting_on: bool, progress_observers: List[ProgressObserver]) -> dict:
        """Proxy function for running a multi-symbol simulation with error capturing."""
        self.__simulator.set_initial_balance(initial_balance)

        if logging_on:
            self.__simulator.enable_logging()
        if reporting_on:
            self.__simulator.enable_reporting()

        results = []
        # run all simulations (using matched progress observer)
        for i, strategy in enumerate(strategies):
            # __run_simulation sets the simulator to use self.strategy
            # we passed in a dummy strategy to satisfy the constructor (self.strategy gets set to dummy)
            # override the dummy strategy in the simulator with the correct one
            self.__simulator.load_strategy(strategy)

            results.append(self.__simulator.run_multiple(symbols, progress_observers[i]))

        return {'results': results}
