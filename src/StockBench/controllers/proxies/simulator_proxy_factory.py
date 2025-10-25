from StockBench.controllers.proxies.simulator_proxy import SimulatorProxy
from StockBench.controllers.simulator.simulator_factory import SimulatorFactory


class SimulatorProxyFactory:
    """Factory for creating SimulatorProxy instances."""

    @staticmethod
    def get_simulator_proxy_instance(simulator_identifier: int) -> SimulatorProxy:
        """Creates a simulator proxy instance."""
        simulator = SimulatorFactory.get_simulator_instance(simulator_identifier)
        return SimulatorProxy(simulator)
