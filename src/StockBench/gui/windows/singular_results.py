import os
import sys

from PyQt6 import QtCore, QtWebEngineWidgets
from PyQt6.QtWidgets import QVBoxLayout, QGridLayout, QHBoxLayout, QWidget, QLabel, QProgressBar, QFrame
from PyQt6.QtCore import QTimer, QThreadPool
from PyQt6 import QtGui

# current directory (peripherals)
current = os.path.dirname(os.path.realpath(__file__))

# parent filepath (src)
parent = os.path.dirname(current)

# add the parent (src) to path
sys.path.append(parent)

from StockBench.display.display import Display


class SingularResultsWindow(QWidget):
    window_stylesheet = """background-color:#202124;"""

    progress_bar_stylesheet = """
    QProgressBar{
        border-radius: 2px;
    }
    
    QProgressBar::chunk{
        border-radius: 2px;
        background-color: #7532a8;
    }"""

    btn_stylesheet = """background-color: #303134;color:#FFF;border-width:0px;border-radius:10px;height:25px;"""

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
        self.unique_chart_saving = False

        self.layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(self.progress_bar_stylesheet)
        self.layout.addWidget(self.progress_bar)

        self.simulation_results_box = SimulationResultsBox()
        self.layout.addWidget(self.simulation_results_box)

        self.setWindowTitle('Simulation Results')
        self.setWindowIcon(QtGui.QIcon('icon/candle.ico'))
        # self.setGeometry(0, 0, 1920, 1080)
        # self.setFixedSize(400, 500)
        self.setStyleSheet(self.window_stylesheet)

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
            # mark the progress bar as completed
            self.progress_bar.setValue(100)

            # stop the timer
            self.timer.stop()
        else:
            # update the progress bar
            self.progress_bar.setValue(int(self.progress_observer.get_progress()))

    def run_simulation(self) -> dict:
        # load the strategy into the simulator
        if self.logging:
            self.simulator.enable_logging()
        if self.reporting:
            self.simulator.enable_reporting()
        self.simulator.load_strategy(self.strategy)
        if self.unique_chart_saving:
            save_option = Display.UNIQUE_SAVE
        else:
            save_option = Display.TEMP_SAVE
        try:
            return self.simulator.run(self.symbol, show_chart=False, save_option=save_option,
                                      progress_observer=self.progress_observer)
        except ValueError as e:
            # pass the error to the simulation results box
            self.simulation_results_box.update_error_message(f'{e}')
            return {}

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
        self.simulation_results_text_box.setMaximumWidth(300)
        self.simulation_results_text_box.setMaximumHeight(800)

        self.webView = QtWebEngineWidgets.QWebEngineView()
        self.layout.addWidget(self.webView)

        self.setLayout(self.layout)

    def render_data(self, simulation_results):
        if 'chart_filepath' in simulation_results:
            self.webView.load(QtCore.QUrl().fromLocalFile(os.path.abspath(simulation_results['chart_filepath'])))
        self.simulation_results_text_box.render_data(simulation_results)

    def update_error_message(self, message):
        # pass the error down to the simulation results text box
        self.simulation_results_text_box.update_error_message(message)


class SimulationResultsTextBox(QFrame):
    title_stylesheet = """color:#FFF;font-size:20px;font-weight:bold;"""

    numeric_results_stylesheet = """color:#FFF;"""

    error_label_style_sheet = """color:#dc143c;margin-top:10px;"""

    def __init__(self):
        super().__init__()

        self.layout = QGridLayout()

        label = QLabel()
        label.setText('Simulation Results')
        label.setStyleSheet(self.title_stylesheet)
        self.layout.addWidget(label, 1, 1)

        # nothing goes in 1, 2 because label 1 is title

        label = QLabel()
        label.setText('Elapsed Time')
        label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(label, 2, 1)

        self.data_label1 = QLabel()
        self.data_label1.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(self.data_label1, 2, 2)

        label = QLabel()
        label.setText('Trades Made')
        label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(label, 3, 1)

        self.data_label2 = QLabel()
        self.data_label2.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(self.data_label2, 3, 2)

        label = QLabel()
        label.setText('Effectiveness')
        label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(label, 4, 1)

        self.data_label3 = QLabel()
        self.data_label3.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(self.data_label3, 4, 2)

        label = QLabel()
        label.setText('Total P/L')
        label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(label, 5, 1)

        self.data_label4 = QLabel()
        self.data_label4.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(self.data_label4, 5, 2)

        label = QLabel()
        label.setText('Average P/L')
        label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(label, 6, 1)

        self.data_label5 = QLabel()
        self.data_label5.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(self.data_label5, 6, 2)

        label = QLabel()
        label.setText('Median P/L')
        label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(label, 7, 1)

        self.data_label6 = QLabel()
        self.data_label6.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(self.data_label6, 7, 2)

        label = QLabel()
        label.setText('Stddev P/L')
        label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(label, 8, 1)

        self.data_label7 = QLabel()
        self.data_label7.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(self.data_label7, 8, 2)

        label = QLabel()
        label.setText('Account Value')
        label.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(label, 9, 1)

        self.data_label8 = QLabel()
        self.data_label8.setStyleSheet(self.numeric_results_stylesheet)
        self.layout.addWidget(self.data_label8, 9, 2)

        self.error_message_box = QLabel()
        self.error_message_box.setStyleSheet(self.error_label_style_sheet)
        self.layout.addWidget(self.error_message_box, 10, 1)

        # stretch the row and column to show natural size
        self.layout.setRowStretch(self.layout.rowCount(), 1)
        self.layout.setColumnStretch(self.layout.columnCount(), 1)

        # apply the layout to the frame
        self.setLayout(self.layout)

        self.__error_message = ""

    def render_data(self, simulation_results: dict):
        if not self.__error_message:
            self.data_label1.setText(f'{simulation_results["elapsed_time"]} seconds')
            self.data_label2.setText(f'{simulation_results["trades_made"]}')
            self.data_label3.setText(f'{simulation_results["effectiveness"]} %')
            self.data_label4.setText(f'$ {simulation_results["total_profit_loss"]}')
            self.data_label5.setText(f'$ {simulation_results["average_profit_loss"]}')
            self.data_label6.setText(f'$ {simulation_results["median_profit_loss"]}')
            self.data_label7.setText(f'$ {simulation_results["standard_profit_loss_deviation"]}')
            self.data_label8.setText(f'$ {simulation_results["account_value"]}')
        else:
            self.error_message_box.setText(f'Error: {self.__error_message}')

    def update_error_message(self, message):
        self.__error_message = message
