import os
import sys
from abc import abstractmethod

from PyQt6 import QtCore, QtWebEngineWidgets
from PyQt6.QtWidgets import QWidget, QProgressBar, QFrame, QLabel, QTabWidget
from PyQt6.QtCore import QTimer, QThreadPool
from PyQt6 import QtGui

# current directory (peripherals)
current = os.path.dirname(os.path.realpath(__file__))

# parent filepath (src)
parent = os.path.dirname(current)

# add the parent (src) to path
sys.path.append(parent)


class SimulationResultsWindow(QWidget):
    """Superclass for a simulation results window."""
    window_stylesheet = """background-color:#202124;"""

    progress_bar_stylesheet = """
        QProgressBar{
            border-radius: 2px;
        }

        QProgressBar::chunk{
            border-radius: 2px;
            background-color: #7532a8;
        }"""
    tab_widget_stylesheet = """
            QTabWidget::pane{
                background-color: #202124;
                border: 0;
            }
            QTabBar::tab:selected {
                color: #ffffff;
                background-color: #42444a;
            }
            QTabBar::tab:!selected {
                color: #ffffff;
                background-color: #323338;
            }"""

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
        self.logging = False
        self.reporting = False
        self.unique_chart_saving = False

        self.setWindowTitle('Simulation Results')
        self.setWindowIcon(QtGui.QIcon(os.path.join('resources', 'images', 'candle.ico')))
        self.setStyleSheet(self.window_stylesheet)

        # define shared attributes here but adding them to layout happens in subclass
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(self.progress_bar_stylesheet)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(self.tab_widget_stylesheet)

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

    @abstractmethod
    def run_simulation(self):
        raise NotImplementedError('You must define an implementation for run_simulation()!')

    @abstractmethod
    def render_updated_data(self, simulation_results: dict):
        raise NotImplementedError('You must define an implementation for render_updated_data()!')

    def update_data(self):
        # create the worker object
        worker = self.worker(self.run_simulation)  # Any other args, kwargs are passed to the run function
        # connect the result (return data) of the qt_worker to the render function to handle the returned data
        worker.signals.result.connect(self.render_updated_data)  # noqa
        # run the qt_worker thread
        self.threadpool.start(worker)


class ResultsFrame(QFrame):
    """Superclass for a results frame."""
    LOADING_REL_PATH = os.path.join('resources', 'default', 'chart_loading.html')
    BACKUP_REL_PATH = os.path.join('resources', 'default', 'chart_unavailable.html')

    def __init__(self):
        super().__init__()

        # define shared attributes here but adding them to layout happens in subclass
        self.webView = QtWebEngineWidgets.QWebEngineView()
        # load blank html file to cover the white screen while the chart loads
        self.render_chart_loading()

    @abstractmethod
    def render_data(self, simulation_results: dict):
        raise NotImplementedError('You must define an implementation for render_data()!')

    @abstractmethod
    def update_error_message(self, message):
        raise NotImplementedError('You must define an implementation for update_data()!')

    def render_chart_loading(self):
        # load the loading html file
        self.webView.load(QtCore.QUrl().fromLocalFile(os.path.abspath(self.LOADING_REL_PATH)))

    def render_chart(self, simulation_results):
        # check the simulation generated a chart
        chart_loaded = False
        if 'chart_filepath' in simulation_results:
            # check the chart exists
            if os.path.isfile(simulation_results['chart_filepath']):
                chart_loaded = True
                self.webView.load(QtCore.QUrl().fromLocalFile(os.path.abspath(simulation_results['chart_filepath'])))

        if not chart_loaded:
            # load the default html file
            self.webView.load(QtCore.QUrl().fromLocalFile(os.path.abspath(self.BACKUP_REL_PATH)))


class ResultsTable(QFrame):
    """Superclass for a results table frame."""
    title_stylesheet = """color:#FFF;font-size:20px;font-weight:bold;"""

    numeric_results_stylesheet = """color:#FFF;"""

    error_label_style_sheet = """color:#dc143c;margin-top:10px;"""

    def __init__(self):
        super().__init__()
        self._error_message = ""

        # Note: this is the only label we can abstract here without PyQt stopp responding error
        self.error_message_box = QLabel()
        self.error_message_box.setWordWrap(True)
        self.error_message_box.setStyleSheet(self.error_label_style_sheet)

    @abstractmethod
    def render_data(self, simulation_results: dict):
        raise NotImplementedError('You must define an implementation for render_data()!')

    def update_error_message(self, message):
        self._error_message = message
