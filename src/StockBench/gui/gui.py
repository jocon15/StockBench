import os
import sys
import json
import time

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QThreadPool, Qt
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

    text_box_stylesheet = """background-color: #303134;color:#FFF;border-width:0px;border-radius:10px;height:25px;
    text-indent:3px;"""

    select_file_btn_stylesheet = """background-color: #303134;color:#FFF;border-width:0px;border-radius:10px;
    height:25px;"""

    combobox_stylesheet = """background-color: #303134;color:#FFF;border-width:0px;border-radius:10px;height:25px;
    text-indent:3px;"""

    line_edit_stylesheet = """background-color:#303134;color:#FFF;border-width:0px;border-radius:10px;height:25px;
    text-indent:5px;"""

    toggle_btn_enabled_stylesheet = """background-color:#04ba5f;display:block;margin-left:auto;margin-right:auto;
    width:40%;height:25px;border-radius:10px;"""

    toggle_btn_disabled_stylesheet = """background-color: #303134;display: block;margin-left: auto;
        margin-right:auto;width: 40%;height:25px;border-radius: 10px;"""

    run_btn_stylesheet = """
        QPushButton
        {
            background-color: #04ba5f;
            color: #FFF;
            border-radius: 10px;
        }
        QPushButton:hover
        {
            background-color: #04ba50;
        }
        """

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

        self.simulation_length = None
        self.simulation_logging = False
        self.simulation_reporting = False
        self.simulation_charting = True

        self.layout = QVBoxLayout()

        label = QLabel()
        label.setText('Strategy:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.strategy_selection_box = StrategySelection()
        self.strategy_selection_box.setStyleSheet(self.select_file_btn_stylesheet)
        self.layout.addWidget(self.strategy_selection_box)

        label = QLabel()
        label.setText('Simulation Length:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.simulation_length_cbox = QComboBox()
        self.simulation_length_cbox.addItem('1 Year')
        self.simulation_length_cbox.addItem('2 Year')
        self.simulation_length_cbox.addItem('5 Year')
        self.simulation_length_cbox.setCurrentIndex(-1)
        self.simulation_length_cbox.setStyleSheet(self.combobox_stylesheet)
        self.simulation_length_cbox.currentIndexChanged.connect(self.on_simulation_length_cbox_index_changed)  # noqa
        self.layout.addWidget(self.simulation_length_cbox)

        label = QLabel()
        label.setText('Simulation Symbol:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.symbol_tbox = QLineEdit()
        self.symbol_tbox.setStyleSheet(self.line_edit_stylesheet)
        self.layout.addWidget(self.symbol_tbox)

        label = QLabel()
        label.setText('Initial Balance:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.balance_tbox = QLineEdit()
        self.onlyFloat = QDoubleValidator()
        self.balance_tbox.setValidator(self.onlyFloat)
        self.balance_tbox.setStyleSheet(self.line_edit_stylesheet)
        self.layout.addWidget(self.balance_tbox)

        label = QLabel()
        label.setText('Logging:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.logging_btn = QPushButton()
        self.logging_btn.setCheckable(True)
        self.logging_btn.setText('OFF')
        self.logging_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)
        self.logging_btn.clicked.connect(self.on_logging_btn_clicked)  # noqa
        self.layout.addWidget(self.logging_btn)

        label = QLabel()
        label.setText('Reporting:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.reporting_btn = QPushButton()
        self.reporting_btn.setCheckable(True)
        self.reporting_btn.setText('OFF')
        self.reporting_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)
        self.reporting_btn.clicked.connect(self.on_reporting_btn_clicked)  # noqa
        self.layout.addWidget(self.reporting_btn)

        label = QLabel()
        label.setText('Charting:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.charting_btn = QPushButton()
        self.charting_btn.setCheckable(True)
        self.charting_btn.setText('ON')
        self.charting_btn.setStyleSheet(self.toggle_btn_enabled_stylesheet)
        self.charting_btn.clicked.connect(self.on_charting_btn_clicked)  # noqa
        self.layout.addWidget(self.charting_btn)

        self.run_btn = QPushButton()
        self.run_btn.setFixedSize(60, 30)
        self.run_btn.setText('RUN')
        self.run_btn.clicked.connect(self.on_run_btn_clicked)  # noqa
        self.run_btn.setStyleSheet(self.run_btn_stylesheet)
        self.layout.addWidget(self.run_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # main window styling
        self.setWindowTitle('Configuration')
        self.setGeometry(200, 200, 400, 500)
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
        background-color: #202124;
        """)

        widget = QWidget()
        widget.setLayout(self.layout)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)

        # build palette object into the windows
        # self.palette = Palette()

        # render the window
        self.show()

    def on_logging_btn_clicked(self):
        if self.logging_btn.isChecked():
            self.simulation_logging = True
            self.logging_btn.setText('ON')
            self.logging_btn.setStyleSheet(self.toggle_btn_enabled_stylesheet)
        else:
            self.simulation_logging = False
            self.logging_btn.setText('OFF')
            self.logging_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)

    def on_reporting_btn_clicked(self):
        if self.reporting_btn.isChecked():
            self.simulation_reporting = True
            self.reporting_btn.setText('ON')
            self.reporting_btn.setStyleSheet(self.toggle_btn_enabled_stylesheet)
        else:
            self.simulation_reporting = False
            self.reporting_btn.setText('OFF')
            self.reporting_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)

    def on_charting_btn_clicked(self):
        if self.charting_btn.isChecked():
            self.simulation_charting = True
            self.charting_btn.setText('ON')
            self.charting_btn.setStyleSheet(self.toggle_btn_enabled_stylesheet)
        else:
            self.simulation_charting = False
            self.charting_btn.setText('OFF')
            self.charting_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)

    def on_simulation_length_cbox_index_changed(self, index):
        if index == 0:
            self.simulation_length = SECONDS_1_YEAR
        elif index == 1:
            self.simulation_length = SECONDS_2_YEAR
        elif index == 2:
            self.simulation_length = SECONDS_5_YEAR

    def on_run_btn_clicked(self):
        # load the strategy from the JSON file into a strategy python dict
        with open(self.strategy_selection_box.strategy_filepath, 'r') as file:
            strategy = json.load(file)

        # inject the unix equivalent dates from the combobox to the dict
        strategy['start'] = int(time.time()) - self.simulation_length
        strategy['end'] = int(time.time())

        # create a new simulations results window
        self.simulation_result_window = SimulationResultsWindow(self.worker, self.simulator, self.progress_bar_observer,
                                                                float(self.balance_tbox.text()))

        # pass the relevant information to the results window by setting its attributes
        self.simulation_result_window.strategy = strategy
        self.simulation_result_window.symbol = self.symbol_tbox.text().upper().strip()
        self.simulation_result_window.logging = self.simulation_logging
        self.simulation_result_window.reporting = self.simulation_reporting
        self.simulation_result_window.charting = self.simulation_charting

        # begin the simulation and progress checking timer
        self.simulation_result_window.begin()

        if self.simulation_charting:
            # show the results window if options is checked
            self.simulation_result_window.show()


class StrategySelection(QWidget):
    def __init__(self):
        super().__init__()

        self.strategy_filepath = None

        self.layout = QHBoxLayout()

        self.filepath_box = QLabel()
        self.filepath_box.setStyleSheet("""background-color: #303134;color: #FFF;""")
        self.layout.addWidget(self.filepath_box)

        self.select_file_btn = QPushButton()
        self.select_file_btn.setText('Select File')
        self.select_file_btn.clicked.connect(self.on_select_file_btn_click)  # noqa
        self.select_file_btn.setStyleSheet("""background-color: #303134;color: #FFF;""")
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
