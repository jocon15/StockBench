import os
from abc import abstractmethod

from StockBench.display.display import Display
from PyQt6.QtWidgets import QWidget, QProgressBar, QTabWidget, QVBoxLayout
from PyQt6.QtCore import QTimer, QThreadPool
from PyQt6 import QtGui


class SimulationResultsWindow(QWidget):
    """Superclass for a simulation results window.

    Once instantiated, the caller must provide

    The simulation is long-running, therefore it is run on a QThread as to not freeze the Qt app while it runs. A
    progress observer (thread-safe) is injected into the simulator to monitor progress of the simulation from this
    window. When the window starts, the simulation is started. A timer is also started to check the progress via the
    progress observer every 100ms. Each interval, the progress is rendered to the window's progress bar to display.

    Once the simulation is complete, the timer is stopped and the progress bar is set to 100%. The simulation returns
    a dict of results which are fed to the render_updated_data() function, which uses that information to render the
    results to the window.
    """
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

        # gets set by child objects
        self.results_frame = None

        self.setWindowTitle('Simulation Results')
        self.setWindowIcon(QtGui.QIcon(os.path.join('resources', 'images', 'candle.ico')))
        self.setStyleSheet(self.window_stylesheet)

        # define layout type
        self.layout = QVBoxLayout()

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
        """Start the window."""
        # the simulation runs 1 time - so no timer, the update data just gets called once
        self.update_data()

        # start the timer to update the progress bar every 100ms
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_progress_bar)  # noqa
        self.timer.start()

    def update_progress_bar(self):
        """Update the progress bar."""
        if self.progress_observer.is_completed():
            # mark the progress bar as completed
            self.progress_bar.setValue(100)

            # stop the timer
            self.timer.stop()
        else:
            # update the progress bar
            self.progress_bar.setValue(int(self.progress_observer.get_progress()))

    def run_simulation(self) -> dict:
        """Run the simulation."""
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
            return self._run_simulation(save_option)
        except ValueError as e:
            # pass the error to the simulation results box
            self.results_frame.update_error_message(f'{e}')
            return {}

    @abstractmethod
    def _run_simulation(self, save_option) -> dict:
        raise NotImplementedError('You must define an implementation for _run_simulation()!')

    @abstractmethod
    def render_updated_data(self, simulation_results: dict):
        raise NotImplementedError('You must define an implementation for render_updated_data()!')

    def update_data(self):
        """Get updated data by running the simulation on a QThread. (different thread from the Qt app)
        This prevents the app from freezing as the long-running simulation is run on a different thread.
        We have a progress observer to keep track of the progress which is used on a timer to update the
        progress bar in the window every 100ms interval until simulation completion.
        """
        # create the worker object
        worker = self.worker(self.run_simulation)  # Any other args, kwargs are passed to the run function
        # connect the result (return data) of the qt_worker to the render function to handle the returned data
        worker.signals.result.connect(self.render_updated_data)  # noqa
        # run the qt_worker thread
        self.threadpool.start(worker)
