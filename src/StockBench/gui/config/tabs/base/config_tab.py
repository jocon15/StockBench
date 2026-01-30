import json
import os.path
import time
from abc import abstractmethod
from functools import wraps
from typing import Callable

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import QPoint

from StockBench.controllers.stockbench_controller import StockBenchController
from StockBench.gui.palette.palette import Palette
from StockBench.gui.studio.strategy_studio import StrategyStudioWindow
from StockBench.controllers.simulator.simulator import Simulator
from StockBench.caching.file_cache import CACHE_FILE_FILEPATH
from StockBench.models.constants.general_constants import *


class MessageBoxCaptureException(Exception):
    """This is a custom exception use with the CaptureErrors decorator."""
    pass


def CaptureConfigErrors(original_fxn: Callable):
    """Decorator for capturing errors. This decorator simply wraps the original function in a try block to capture
    raised exceptions that are designated as MassageBoxCaptureExceptions. If such an exception occurs, the exception
    message is logged to the tab's error_message_box instead of crashing the program.

    This decorator allows for the functionalization of validation logic without having to use try blocks or return
    a status value. Functions that contain paths that require an error message to be shown simply need to decorate
    using @CaptureErrors and raise MessageBoxCaptureExceptions with a custom message for the message box.
    """
    @wraps(original_fxn)
    def wrapper(self, *args, **kwargs):
        try:
            return original_fxn(self, *args, **kwargs)
        except MessageBoxCaptureException as e:
            self.error_message_box.setText(str(e))
            self.layout.addWidget(self.error_message_box)
    return wrapper


class ConfigTab(QWidget):
    """Abstract base class for a configuration tab."""
    ON = 'ON'
    OFF = 'OFF'

    DEFAULT_CACHE_KEY = 'cached_strategy_filepath'

    def __init__(self, stockbench_controller: StockBenchController):
        super().__init__()
        self._stockbench_controller = stockbench_controller

        # windows launched from a class need to be attributes or else they will be closed when the function
        # scope that called them is exited
        self.simulation_result_window = None
        self.strategy_studio_window = None

        self.simulation_length = None
        self.simulation_logging = False
        self.simulation_reporting = False
        self.simulation_unique_chart_saving = False
        self.head_to_head_window = None
        self.results_depth = Simulator.CHARTS_AND_DATA

        # ========================= Shared Components ================================
        self.layout = QVBoxLayout()

        self.run_btn = QPushButton()
        self.run_btn.setFixedSize(60, 30)
        self.run_btn.setText('RUN')
        self.run_btn.clicked.connect(self.on_run_btn_clicked)  # noqa
        self.run_btn.setStyleSheet(Palette.RUN_BTN_STYLESHEET)

        self.error_message_box = QLabel()
        self.error_message_box.setStyleSheet(Palette.ERROR_LABEL_STYLESHEET)

    @CaptureConfigErrors
    def on_strategy_studio_btn_clicked(self, filepath: str):
        """
        Decorator:
            The CaptureErrors decorator allows custom exceptions to be caught and logged to the error message box
            instead of crashing. It also allows us to functionalize the filepath validation without the need for
            try blocks or return values.
        """
        self._validate_filepath(filepath)

        # launch the strategy studio window injecting the filepath from the filepath box into the strategy editor
        coordinates = self.mapToGlobal(QPoint(0, 0))
        self.strategy_studio_window = StrategyStudioWindow(
            filepath,
            coordinates,
            self.width()
        )
        self.strategy_studio_window.show()

    def on_simulation_length_cbox_index_changed(self, index):
        if index == 0:
            self.simulation_length = SECONDS_1_YEAR
        elif index == 1:
            self.simulation_length = SECONDS_2_YEAR
        elif index == 2:
            self.simulation_length = SECONDS_5_YEAR

    def on_logging_btn_clicked(self, button: QPushButton):
        """Handles logging button toggle. Button reference is passed so we can read/update the button
        at this level despite it being buried under layers of QFrames."""
        if button.isChecked():
            self.simulation_logging = True
            button.setText(self.ON)
            button.setStyleSheet(Palette.TOGGLE_BTN_ENABLED_STYLESHEET)
        else:
            self.simulation_logging = False
            button.setText(self.OFF)
            button.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)

    def on_reporting_btn_clicked(self, button: QPushButton):
        """Handles reporting button toggle. Button reference is passed so we can read/update the button
        at this level despite it being buried under layers of QFrames."""
        if button.isChecked():
            self.simulation_reporting = True
            button.setText(self.ON)
            button.setStyleSheet(Palette.TOGGLE_BTN_ENABLED_STYLESHEET)
        else:
            self.simulation_reporting = False
            button.setText(self.OFF)
            button.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)

    def on_chart_saving_btn_clicked(self, button: QPushButton):
        """Handles chart saving button toggle. Button reference is passed so we can read/update the button
        at this level despite it being buried under layers of QFrames."""
        if button.isChecked():
            self.simulation_unique_chart_saving = True
            button.setText(self.ON)
            button.setStyleSheet(Palette.TOGGLE_BTN_ENABLED_STYLESHEET)
        else:
            self.simulation_unique_chart_saving = False
            button.setText(self.OFF)
            button.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)

    def data_and_charts_btn_selected(self, selected):
        if selected:
            self.results_depth = Simulator.CHARTS_AND_DATA

    def data_only_btn_selected(self, selected):
        if selected:
            self.results_depth = Simulator.DATA_ONLY

    @CaptureConfigErrors
    def load_strategy(self, filepath: str, cache_key=None, cache_value=None):
        """Loads a strategy from a filepath.

        Decorator:
            The CaptureErrors decorator allows custom exceptions to be caught and logged to the error message box
            instead of crashing. It also allows us to functionalize the filepath validation without the need for
            try blocks or return values.
        """
        self._validate_filepath(filepath)
        try:
            with open(filepath, 'r') as file:
                strategy = json.load(file)
        except Exception as e:
            raise MessageBoxCaptureException(f'Uncaught error parsing strategy file: {e}')

        # cache the strategy filepath (create if it does not already exist)
        self.cache_strategy_filepath(filepath, cache_key, cache_value)

        # inject the unix equivalent dates from the combobox to the dict
        strategy['strategy_filepath'] = filepath
        strategy[START_KEY] = int(time.time()) - self.simulation_length
        strategy[END_KEY] = int(time.time())

        return strategy

    def cache_strategy_filepath(self, strategy_filepath, cache_key=None, cache_value=None):
        # cache the strategy filepath (create if it does not already exist)

        key = self.DEFAULT_CACHE_KEY
        if cache_key:
            key = cache_key

        # get the existing cache data
        with open(CACHE_FILE_FILEPATH, 'r') as file:
            data = json.load(file)

        # add the filepath to the cache data
        if cache_value:
            data[key] = cache_value
        else:
            data[key] = strategy_filepath

        # write the cache data
        with open(CACHE_FILE_FILEPATH, 'w+') as file:
            json.dump(data, file)

    @staticmethod
    def _validate_filepath(filepath: str):
        if filepath is None or filepath == '':
            raise MessageBoxCaptureException('You must select a strategy file!')
        if not os.path.isfile(filepath):
            raise MessageBoxCaptureException('Strategy filepath is not a valid file!')

    @abstractmethod
    def on_run_btn_clicked(self, clicked_signal: bool):
        raise NotImplementedError('You need to implement this method!')
