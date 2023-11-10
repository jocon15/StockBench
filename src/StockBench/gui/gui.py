import os
import sys

from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QProgressBar
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import QTimer, QThreadPool
from PyQt6.QtGui import QBrush

# current directory (peripherals)
current = os.path.dirname(os.path.realpath(__file__))

# parent filepath (src)
parent = os.path.dirname(current)

# add the parent (src) to path
sys.path.append(parent)

from worker.worker import Worker
from StockBench.observers.progress_observer import ProgressObserver
from StockBench.simulator import Simulator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Note: this must be declared before everything else so that the thread pool exists before we attempt to use it
        self.threadpool = QThreadPool()

        # FIXME: since sim results window calls run(), this has to be passed to the sim results window to avoid
        #   circular import error (maybe just pass class reference to window and let the window instantiate?)
        self.progress_bar_observer = ProgressObserver
        # pass an uninitialized reference of the worker object to the windows
        self.worker = Worker
        # pass an uninitialized reference of the simulator object to the windows
        self.simulator = Simulator

        self.layout = QVBoxLayout()

        # FIXME add the widgets to the layout

        widget = QWidget()
        widget.setLayout(self.layout)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)

        # build palette object into the windows
        # self.palette = Palette()

        # render the window
        self.show()
