from StockBench.controllers.charting.multi.multi_charting_engine import MultiChartingEngine
from StockBench.controllers.charting.singular.singular_charting_engine import SingularChartingEngine
from StockBench.controllers.simulator.simulator import Simulator
from StockBench.controllers.stockbench_controller import StockBenchController


class StockBenchControllerFactory:
    """Creates a StockBenchController instance."""

    @staticmethod
    def get_controller_instance() -> StockBenchController:
        simulator = Simulator()
        singular_charting_engine = SingularChartingEngine()
        multi_charting_engine = MultiChartingEngine()
        return StockBenchController(simulator, singular_charting_engine, multi_charting_engine)
