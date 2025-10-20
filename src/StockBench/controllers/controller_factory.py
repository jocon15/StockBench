from StockBench.controllers.charting.singular.singular_charting_engine import SingularChartingEngine
from StockBench.controllers.simulator.simulator import Simulator
from StockBench.controllers.stockbench_controller import StockBenchController


class StockBenchControllerFactory:
    """Creates a StockBenchController instance."""

    @staticmethod
    def get_controller_instance() -> StockBenchController:
        simulator = Simulator()
        charting_engine = SingularChartingEngine()
        return StockBenchController(simulator, charting_engine)
