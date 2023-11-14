import os
import sys

from PyQt6 import QtCore, QtWebEngineWidgets
from PyQt6.QtWidgets import QVBoxLayout, QGridLayout, QHBoxLayout, QWidget, QLabel, QProgressBar, QFrame
from PyQt6.QtCore import QTimer, QThreadPool

# current directory (peripherals)
current = os.path.dirname(os.path.realpath(__file__))

# parent filepath (src)
parent = os.path.dirname(current)

# add the parent (src) to path
sys.path.append(parent)


class SimulationResultsWindow(QWidget):
    def __init__(self, worker, simulator, progress_observer, initial_balance):
        super().__init__()
        # Note: this must be declared before everything else so that the thread pool exists before we attempt to use it
        self.threadpool = QThreadPool()

        # parameters
        self.worker = worker
        self.simulator = simulator(initial_balance)  # instantiate the class reference
        self.progress_observer = progress_observer()  # instantiate the class reference

        # get set by caller (MainWindow) after construction but before .show()
        self.strategy = None
        self.symbol = None
        self.logging = False
        self.reporting = False
        self.charting = False

        self.layout = QVBoxLayout()

        # FIXME: add elements to layout
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setTextVisible(False)
        self.layout.addWidget(self.progress_bar)

        self.simulation_results_box = SimulationResultsBox()
        self.layout.addWidget(self.simulation_results_box)

        # FIXME: still need the done button at the bottom

        # apply the layout to the window
        self.setLayout(self.layout)

        # timer to periodically read from the progress observer and update the progress bar
        self.timer = QTimer()

    def begin(self):
        # the simulation runs 1 time - so no timer, the update data just gets called once
        self.update_data()

        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_progress_bar)  # noqa
        self.timer.start()

    def update_progress_bar(self):
        if self.progress_observer.is_completed():
            # the progress is complete, stop the timer
            self.timer.stop()
        # update the progress bar
        self.progress_bar.setValue(int(self.progress_observer.get_progress()))

    def run_simulation(self) -> dict:
        # load the strategy into the simulator
        self.simulator.load_strategy(self.strategy)
        return self.simulator.run(self.symbol, show_chart=False, save_chart=True,
                                  progress_observer=self.progress_observer)

    def render_updated_data(self, simulation_results: dict):
        self.simulation_results_box.render_data(simulation_results)

    def update_data(self):
        # create the worker object
        worker = self.worker(self.run_simulation)  # Any other args, kwargs are passed to the run function
        # connect the result (return data) of the qt_worker to the render function to handle the returned data
        worker.signals.result.connect(self.render_updated_data)  # noqa
        # run the qt_worker thread
        self.threadpool.start(worker)


class SimulationResultsBox(QFrame):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()

        self.simulation_results_text_box = SimulationResultsTextBox()
        self.layout.addWidget(self.simulation_results_text_box)

        self.webView = QtWebEngineWidgets.QWebEngineView()
        self.layout.addWidget(self.webView)

        self.setLayout(self.layout)

    def render_data(self, simulation_results):
        self.webView.load(QtCore.QUrl().fromLocalFile(os.path.abspath(simulation_results['chart_filepath'])))
        self.simulation_results_text_box.render_data(simulation_results)


class SimulationResultsTextBox(QFrame):
    def __init__(self):
        super().__init__()

        self.layout = QGridLayout()

        label = QLabel()
        label.setText('Simulation Results')
        # label.setStyleSheet("""""")
        self.layout.addWidget(label, 1, 1)

        # nothing goes in 1, 2 because label 1 is title

        label = QLabel()
        label.setText('Elapsed Time:')
        # label.setStyleSheet("""""")
        self.layout.addWidget(label, 2, 1)

        self.data_label1 = QLabel()
        # label.setStyleSheet("""""")
        self.layout.addWidget(self.data_label1, 2, 2)

        label = QLabel()
        label.setText('Trades Made:')
        # label.setStyleSheet("""""")
        self.layout.addWidget(label, 3, 1)

        self.data_label2 = QLabel()
        # label.setStyleSheet("""""")
        self.layout.addWidget(self.data_label2, 3, 2)

        label = QLabel()
        label.setText('Effectiveness:')
        # label.setStyleSheet("""""")
        self.layout.addWidget(label, 4, 1)

        self.data_label3 = QLabel()
        # label.setStyleSheet("""""")
        self.layout.addWidget(self.data_label3, 4, 2)

        label = QLabel()
        label.setText('Avg. P/L:')
        # label.setStyleSheet("""""")
        self.layout.addWidget(label, 5, 1)

        self.data_label4 = QLabel()
        # label.setStyleSheet("""""")
        self.layout.addWidget(self.data_label4, 5, 2)

        label = QLabel()
        label.setText('Total P/L:')
        # label.setStyleSheet("""""")
        self.layout.addWidget(label, 6, 1)

        self.data_label5 = QLabel()
        # label.setStyleSheet("""""")
        self.layout.addWidget(self.data_label5, 6, 2)

        label = QLabel()
        label.setText('Account Value:')
        # label.setStyleSheet("""""")
        self.layout.addWidget(label, 7, 1)

        self.data_label6 = QLabel()
        # label.setStyleSheet("""""")
        self.layout.addWidget(self.data_label6, 7, 2)

        # apply the layout to the frame
        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        self.data_label1.setText(f'{simulation_results["elapsed_time"]} seconds')

        self.data_label2.setText(f'{simulation_results["trades_made"]}')

        self.data_label3.setText(f'{simulation_results["effectiveness"]}')

        self.data_label4.setText(f'{simulation_results["average_profit_loss"]}')

        self.data_label5.setText(f'{simulation_results["total_profit_loss"]}')

        self.data_label6.setText(f'{simulation_results["account_value"]}')
