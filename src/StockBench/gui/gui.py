import os
import sys
import json
import time

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QThreadPool
from PyQt6.QtGui import QDoubleValidator

# current directory (peripherals)
current = os.path.dirname(os.path.realpath(__file__))

# parent filepath (src)
parent = os.path.dirname(current)

# add the parent (src) to path
sys.path.append(parent)

from StockBench.gui.worker.worker import Worker
from StockBench.observers.progress_observer import ProgressObserver
from StockBench.simulator import Simulator
from StockBench.gui.windows.simulation_results import SimulationResultsWindow
from StockBench.constants import *


class MainWindow(QMainWindow):
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

        self.simulation_length = None
        self.simulation_logging = False
        self.simulation_reporting = False
        self.simulation_charting = False

        self.layout = QVBoxLayout()

        label = QLabel()
        label.setText('Strategy:')
        self.layout.addWidget(label)

        self.strategy_selection_box = StrategySelection()
        self.layout.addWidget(self.strategy_selection_box)

        label = QLabel()
        label.setText('Simulation Length:')
        self.layout.addWidget(label)

        self.simulation_length_cbox = QComboBox()
        self.simulation_length_cbox.addItem('1 Year')
        self.simulation_length_cbox.addItem('2 Year')
        self.simulation_length_cbox.addItem('5 Year')
        self.simulation_length_cbox.setCurrentIndex(-1)
        self.simulation_length_cbox.currentIndexChanged.connect(self.on_simulation_length_cbox_index_changed)  # noqa
        self.layout.addWidget(self.simulation_length_cbox)

        label = QLabel()
        label.setText('Simulation Symbol:')
        self.layout.addWidget(label)

        self.symbol_tbox = QLineEdit()
        self.layout.addWidget(self.symbol_tbox)

        label = QLabel()
        label.setText('Initial Balance:')
        self.layout.addWidget(label)

        self.balance_tbox = QLineEdit()
        self.onlyFloat = QDoubleValidator()
        self.balance_tbox.setValidator(self.onlyFloat)
        self.layout.addWidget(self.balance_tbox)

        label = QLabel()
        label.setText('Logging:')
        self.layout.addWidget(label)

        self.logging_btn = QPushButton()
        self.layout.addWidget(self.logging_btn)

        label = QLabel()
        label.setText('Reporting:')
        self.layout.addWidget(label)

        self.logging_btn = QPushButton()
        self.layout.addWidget(self.logging_btn)

        label = QLabel()
        label.setText('Charting:')
        self.layout.addWidget(label)

        self.logging_btn = QPushButton()
        self.layout.addWidget(self.logging_btn)

        self.run_btn = QPushButton()
        self.run_btn.setText('RUN')
        self.run_btn.clicked.connect(self.on_run_btn_clicked)  # noqa
        self.layout.addWidget(self.run_btn)

        widget = QWidget()
        widget.setLayout(self.layout)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)

        # build palette object into the windows
        # self.palette = Palette()

        # render the window
        self.show()

    def on_simulation_length_cbox_index_changed(self, index):
        if index == 0:
            self.simulation_length = SECONDS_1_YEAR

    def on_run_btn_clicked(self):
        # load the strategy from the JSON file into a strategy python dict
        with open(self.strategy_selection_box.strategy_filepath, 'r') as file:
            strategy = json.load(file)

        # inject the unix equivalent dates from the combobox to the dict
        strategy['start'] = int(time.time()) - self.simulation_length
        strategy['end'] = int(time.time())

        # create a new simulations results window
        simulation_result_window = SimulationResultsWindow(self.worker, self.simulator, self.progress_bar_observer,
                                                           float(self.balance_tbox.text()))

        # pass the relevant information to the results window by setting its attributes
        simulation_result_window.strategy = strategy
        simulation_result_window.symbol = self.symbol_tbox.text().upper().strip()
        simulation_result_window.logging = self.simulation_logging
        simulation_result_window.reporting = self.simulation_reporting
        simulation_result_window.charting = self.simulation_charting

        # begin the simulation and progress checking timer
        simulation_result_window.begin()

        # show the results window
        simulation_result_window.show()


class StrategySelection(QWidget):
    def __init__(self):
        super().__init__()

        self.strategy_filepath = None

        self.layout = QHBoxLayout()

        self.filepath_box = QLabel()
        self.layout.addWidget(self.filepath_box)

        self.select_file_btn = QPushButton()
        self.select_file_btn.setText('Select File')
        self.select_file_btn.clicked.connect(self.on_select_file_btn_click)  # noqa
        self.layout.addWidget(self.select_file_btn)

        self.setLayout(self.layout)

    def on_select_file_btn_click(self):
        dlg = QFileDialog()
        # dlg.setFileMode(QFileDialog.)
        # dlg.setFilter("Text files (*.json)")
        if dlg.exec():
            filenames = dlg.selectedFiles()
            self.strategy_filepath = filenames[0]
            self.filepath_box.setText(self.strategy_filepath)
