import os

from StockBench.controllers.simulator.broker.broker_client import BrokerClient
from StockBench.controllers.simulator.broker.configuration import BrokerConfiguration
from StockBench.controllers.simulator.simulator import Simulator


class SimulatorFactory:
    """Factory for creating simulator instances."""
    @staticmethod
    def get_simulator_instance(simulator_identifier: int = 1) -> Simulator:
        """Creates an instance of a simulator."""
        config = BrokerConfiguration(
            os.environ.get('ALPACA_API_KEY'),
            os.environ.get('ALPACA_SECRET_KEY'))

        return Simulator(BrokerClient(config), simulator_identifier)
