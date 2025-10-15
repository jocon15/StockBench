import logging
import traceback
from abc import abstractmethod

import requests.exceptions

from StockBench.controllers.broker.broker_client import InvalidSymbolError, InsufficientDataError, MissingCredentialError
from StockBench.controllers.charting import ChartingEngine
from PyQt6.QtWidgets import QWidget, QProgressBar, QTabWidget, QVBoxLayout
from PyQt6.QtCore import QTimer, QThreadPool
from PyQt6 import QtGui

from StockBench.gui.models.simulation_results_bundle import SimulationResultsBundle
from StockBench.gui.palette.palette import Palette
from StockBench.gui.worker.worker import Worker
from StockBench.observers.progress_observer import ProgressObserver
from StockBench.controllers.simulator import Simulator
from StockBench.controllers.indicator import StrategyIndicatorError
from StockBench.controllers.charting.exceptions import ChartingError
from StockBench.controllers.algorithm import MalformedStrategyError

log = logging.getLogger()


class SimulationResultsWindow(QWidget):
    """Abstract base class for a simulation results window.

    After instantiation, the caller must call the 'begin()' function to start the simulation and progress observer
    timer. If the user deselects the option to view the results, this window never gets shown because this window's show
    command is delegated to the caller, meaning the caller has control over whether this window actually gets shown.

    The simulation is long-running, therefore it is run on a QThread as to not freeze the Qt app while it runs. A
    progress observer (thread-safe) is injected into the simulator to monitor progress of the simulation from this
    window. When the window starts, the simulation is started. A timer is also started to check the progress via the
    progress observer every 100ms. Each interval, the progress is rendered to the window's progress bar to charting.

    Once the simulation is complete, the timer is stopped and the progress bar gets set to 100%. The simulation returns
    a dict of results which are fed to the _render_data() function, which uses that information to render the results to
    the window.
    """

    def __init__(self, strategy, initial_balance, logging_on=False, reporting_on=False, unique_chart_saving_on=False,
                 show_volume=False, results_depth=Simulator.CHARTS_AND_DATA, identifier: int = 1):
        super().__init__()
        self.id = identifier
        self.strategy = strategy
        self.simulator = Simulator(initial_balance, identifier)  # instantiate the class reference
        self.progress_observer = ProgressObserver()  # instantiate the class reference
        self.worker = Worker  # gets instantiated later
        self.logging = logging_on
        self.reporting = reporting_on
        self.unique_chart_saving = unique_chart_saving_on
        self.show_volume = show_volume
        self.results_depth = results_depth

        # Note: this must be declared before everything else so that the thread pool exists before we attempt to use it
        self.threadpool = QThreadPool()

        # gets set by child objects
        self.overview_tab = None

        self.setWindowTitle('Simulation Results')
        self.setWindowIcon(QtGui.QIcon(Palette.CANDLE_ICON))
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
        self.timer.timeout.connect(self._update_progress_bar)  # noqa
        self.timer.start()

    def _update_progress_bar(self):
        """Update the progress bar."""
        if self.progress_observer.is_simulation_completed():
            # mark the progress bar as completed
            self.progress_bar.setValue(100)

            # stop the timer
            self.timer.stop()
        else:
            # update the progress bar
            self.progress_bar.setValue(int(self.progress_observer.get_progress()))

    def __run_simulation(self) -> SimulationResultsBundle:
        """Run the simulation."""
        # set up the simulator's configuration options
        if self.logging:
            self.simulator.enable_logging()
        if self.reporting:
            self.simulator.enable_reporting()

        # configure the simulator's configuration options
        if self.unique_chart_saving:
            save_option = ChartingEngine.UNIQUE_SAVE
        else:
            save_option = ChartingEngine.TEMP_SAVE

        # load the strategy file
        self.simulator.load_strategy(self.strategy)

        # run the simulation and catch any errors - keep the app from crashing even if the sim fails
        try:
            return self._run_simulation(save_option, self.results_depth)
        except requests.exceptions.ConnectionError:
            message = 'Failed to connect to broker!'
        except MalformedStrategyError as e:
            message = f'Malformed strategy error: {e}'
        except StrategyIndicatorError as e:
            message = f'Strategy error: {e}'
        except ChartingError as e:
            message = f'Charting error: {e}'
        except MissingCredentialError as e:
            message = f'Missing credential error: {e}'
        except InvalidSymbolError as e:
            message = f'Invalid symbol error: {e}'
        except InsufficientDataError as e:
            message = f'Insufficient data error {e}'
        except Exception as e:
            message = f'Unexpected error: {type(e)} {e} {traceback.print_exc()}'
        # WARNING, trying to interact with UI components here (calling a custom abstract signature) will not work
        # because the simulation is on a different QThread and will cause crash with no traceback, you must instead take
        # any simulation failure action in the _render_data implementation because _render_data is the callback called
        # by the QThread when it is done, success or failure.

        # log all errors and display error message in console box
        log.error(message)
        self.overview_tab.update_error_message(message)
        return SimulationResultsBundle({}, {})

    @abstractmethod
    def _run_simulation(self, save_option: int, results_depth: int) -> SimulationResultsBundle:
        raise NotImplementedError('You must define an implementation for _run_simulation()!')

    @abstractmethod
    def _render_data(self, simulation_results_bundle: SimulationResultsBundle):
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
