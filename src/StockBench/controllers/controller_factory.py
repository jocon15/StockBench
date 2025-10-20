from StockBench.controllers.charting.folder.folder_charting_engine import FolderChartingEngine
from StockBench.controllers.charting.multi.multi_charting_engine import MultiChartingEngine
from StockBench.controllers.charting.singular.singular_charting_engine import SingularChartingEngine
from StockBench.controllers.simulator.simulator import Simulator
from StockBench.controllers.stockbench_controller import StockBenchController


class StockBenchControllerFactory:
    """Creates a StockBenchController instance."""

    @staticmethod
    def get_controller_instance(simulation_identifier: int = 1) -> StockBenchController:
        simulator = Simulator(simulation_identifier)
        singular_charting_engine = SingularChartingEngine()
        multi_charting_engine = MultiChartingEngine()
        folder_charting_engine = FolderChartingEngine()
        return StockBenchController(simulator, singular_charting_engine, multi_charting_engine, folder_charting_engine)
