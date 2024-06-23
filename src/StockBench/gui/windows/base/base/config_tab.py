import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QThreadPool

from StockBench.gui.worker.worker import Worker
from StockBench.observers.progress_observer import ProgressObserver
from StockBench.simulator import Simulator


class ConfigTab(QWidget):
    def __init__(self):
        super().__init__()
        # Note: this must be declared before everything else so that the thread pool exists before we attempt to use it
        self.threadpool = QThreadPool()

        # since sim results window calls run(), this has to be passed to the sim results window to avoid
        #   circular import error (maybe just pass class reference to window and let the window instantiate?)
        self.progress_bar_observer = ProgressObserver
        # pass an uninitialized reference of the worker object to the windows
        self.worker = Worker
        # pass an uninitialized reference of the simulator object to the windows
        self.simulator = Simulator

        # windows launched from a class need to be attributes or else they will be closed when the function
        # scope that called them is exited
        self.simulation_result_window = None
        self.strategy_studio_window = None

        self.simulation_length = None
        self.simulation_logging = False
        self.simulation_reporting = False
        self.simulation_unique_chart_saving = False
        self.simulation_show_results_window = True

        self.layout = QVBoxLayout()

    @staticmethod
    def cache_strategy_filepath(strategy_filepath):
        # cache the strategy filepath (create if it does not already exist)
        data = {'cached_strategy_filepath': strategy_filepath}
        with open('cache.json', 'w+') as file:
            json.dump(data, file)
