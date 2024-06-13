import os
import logging
from abc import abstractmethod

from StockBench.display.display import Display
from PyQt6.QtWidgets import QWidget, QProgressBar, QTabWidget, QVBoxLayout
from PyQt6.QtCore import QTimer, QThreadPool
from PyQt6 import QtGui
from StockBench.gui.palette.palette import Palette

log = logging.getLogger()


class SimulationResultsWindow(QWidget):
    """Abstract base class for a simulation results window.

    After instantiation, the caller must call the 'begin()' function to start the simulation and progress observer
    timer. If the user deselects the option to view the results, this window never gets shown because this window's show
    command is delegated to the caller, meaning the caller has control over whether this window actually gets shown.

    The simulation is long-running, therefore it is run on a QThread as to not freeze the Qt app while it runs. A
    progress observer (thread-safe) is injected into the simulator to monitor progress of the simulation from this
    window. When the window starts, the simulation is started. A timer is also started to check the progress via the
    progress observer every 100ms. Each interval, the progress is rendered to the window's progress bar to display.

    Once the simulation is complete, the timer is stopped and the progress bar gets set to 100%. The simulation returns
    a dict of results which are fed to the _render_data() function, which uses that information to render the results to
    the window.
    """

    def __init__(self, strategy, initial_balance, simulator, progress_observer, worker, logging_on=False,
                 reporting_on=False, unique_chart_saving_on=False):
        super().__init__()
        self.strategy = strategy
        self.simulator = simulator(initial_balance)  # instantiate the class reference
        self.progress_observer = progress_observer()  # instantiate the class reference
        self.worker = worker
        self.logging = logging_on
        self.reporting = reporting_on
        self.unique_chart_saving = unique_chart_saving_on

        # Note: this must be declared before everything else so that the thread pool exists before we attempt to use it
        self.threadpool = QThreadPool()

        # gets set by child objects
        self.results_frame = None

        self.setWindowTitle('Simulation Results')
        self.setWindowIcon(QtGui.QIcon(os.path.join('resources', 'images', 'candle.ico')))
        self.setStyleSheet(Palette.WINDOW_STYLESHEET)

        # define layout type
        self.layout = QVBoxLayout()

        # define shared attributes here but adding them to layout happens in subclass
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(Palette.PROGRESS_BAR_STYLESHEET)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(Palette.TAB_WIDGET_STYLESHEET)

        # timer to periodically read from the progress observer and update the progress bar
        self.timer = QTimer()

    def begin(self):
        """Starts the simulation and window's progress bar updater timer."""
        # the simulation runs 1 time - so no timer, the update data just gets called once
        self.__update_data()

        # start the timer to update the progress bar every 100ms
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.__update_progress_bar)  # noqa
        self.timer.start()

    def __update_progress_bar(self):
        """Update the progress bar."""
        if self.progress_observer.is_simulation_completed():
            # mark the progress bar as completed
            self.progress_bar.setValue(100)

            # stop the timer
            self.timer.stop()
        else:
            # update the progress bar
            self.progress_bar.setValue(int(self.progress_observer.get_progress()))

    def __run_simulation(self) -> dict:
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
            # pass the known error down
            self.results_frame.update_error_message(f'{e}')
            return {}
        except Exception as e:
            # unexpected error
            log.error(f'Unexpected error during simulation: {e}')
            self.results_frame.update_error_message(f'Unexpected error: {e}')
            return {}

    @abstractmethod
    def _run_simulation(self, save_option) -> dict:
        raise NotImplementedError('You must define an implementation for _run_simulation()!')

    @abstractmethod
    def _render_data(self, simulation_results: dict):
        raise NotImplementedError('You must define an implementation for _render_data()!')

    def __update_data(self):
        """Get updated data by running the simulation on a QThread. (different thread from the Qt app)
        This prevents the app from freezing as the long-running simulation is run on a different thread.
        We have a progress observer to keep track of the progress which is used on a timer to update the
        progress bar in the window every 100ms interval until simulation completion.
        """
        # create the worker object
        worker = self.worker(self.__run_simulation)  # Any other args, kwargs are passed to the run function
        # connect the result (return data) of the qt_worker to the render function to handle the returned data
        worker.signals.result.connect(self._render_data)  # noqa
        # run the qt_worker thread
        self.threadpool.start(worker)
