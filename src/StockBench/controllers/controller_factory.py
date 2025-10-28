from StockBench.controllers.proxies.charting_proxy_factory import ChartingProxyFactory
from StockBench.controllers.proxies.simulator_proxy_factory import SimulatorProxyFactory
from StockBench.controllers.stockbench_controller import StockBenchController


class StockBenchControllerFactory:
    """Factory for creating StockBenchController instances."""

    @staticmethod
    def get_controller_instance(identifier: int = 1) -> StockBenchController:
        """Creates a controller instance."""
        simulator_proxy = SimulatorProxyFactory.get_simulator_proxy_instance(identifier)
        charting_proxy = ChartingProxyFactory.get_charting_proxy_instance(identifier)
        return StockBenchController(simulator_proxy, charting_proxy)
