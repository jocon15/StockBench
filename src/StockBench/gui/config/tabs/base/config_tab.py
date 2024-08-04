import json
import time
from abc import abstractmethod

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QComboBox
from PyQt6.QtCore import QThreadPool
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import QPoint

from StockBench.gui.worker.worker import Worker
from StockBench.observers.progress_observer import ProgressObserver
from StockBench.gui.palette.palette import Palette
from StockBench.gui.studio.strategy_studio import StrategyStudioWindow
from StockBench.constants import *
from StockBench.simulator import Simulator


class ConfigTab(QWidget):
    CACHE_FILE_FILEPATH = 'cache.json'

    DEFAULT_CACHE_KEY = 'cached_strategy_filepath'

    def __init__(self, palette: Palette):
        super().__init__()
        self.palette = palette

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
        self.strategy_studio_window = None

        self.simulation_length = None
        self.simulation_logging = False
        self.simulation_reporting = False
        self.simulation_unique_chart_saving = False
        self.simulation_show_results_window = True
        self.head_to_head_window = None
        self.results_depth = Simulator.CHARTS_AND_DATA

        # ========================= Shared Components ================================
        # define the layout
        self.layout = QVBoxLayout()

        # simulation length label
        self.simulation_length_label = QLabel()
        self.simulation_length_label.setText('Simulation Length:')
        self.simulation_length_label.setStyleSheet(self.palette.INPUT_LABEL_STYLESHEET)
        # simulation length input
        self.simulation_length_cbox = QComboBox()
        self.simulation_length_cbox.addItem('1 Year')
        self.simulation_length_cbox.addItem('2 Year')
        self.simulation_length_cbox.addItem('5 Year')
        # set simulation length default to 2 years (must set attribute as well)
        self.simulation_length_cbox.setCurrentIndex(1)
        self.simulation_length = SECONDS_2_YEAR
        self.simulation_length_cbox.setStyleSheet(self.palette.COMBOBOX_STYLESHEET)
        self.simulation_length_cbox.currentIndexChanged.connect(self.on_simulation_length_cbox_index_changed)  # noqa

        # initial balance label
        self.initial_balance_label = QLabel()
        self.initial_balance_label.setText('Initial Balance:')
        self.initial_balance_label.setStyleSheet(self.palette.INPUT_LABEL_STYLESHEET)
        # initial balance input
        self.initial_balance_tbox = QLineEdit()
        self.initial_balance_tbox.setText('1000.0')
        self.onlyFloat = QDoubleValidator()
        self.initial_balance_tbox.setValidator(self.onlyFloat)
        self.initial_balance_tbox.setStyleSheet(self.palette.LINE_EDIT_STYLESHEET)

        # logging label
        self.logging_label = QLabel()
        self.logging_label.setText('Logging:')
        self.logging_label.setStyleSheet(self.palette.INPUT_LABEL_STYLESHEET)
        # logging button
        self.logging_btn = QPushButton()
        self.logging_btn.setCheckable(True)
        self.logging_btn.setText('OFF')
        self.logging_btn.setStyleSheet(self.palette.TOGGLE_BTN_DISABLED_STYLESHEET)
        self.logging_btn.clicked.connect(self.on_logging_btn_clicked)  # noqa

        # reporting label
        self.reporting_label = QLabel()
        self.reporting_label.setText('Reporting:')
        self.reporting_label.setStyleSheet(self.palette.INPUT_LABEL_STYLESHEET)
        # reporting button
        self.reporting_btn = QPushButton()
        self.reporting_btn.setCheckable(True)
        self.reporting_btn.setText('OFF')
        self.reporting_btn.setStyleSheet(self.palette.TOGGLE_BTN_DISABLED_STYLESHEET)
        self.reporting_btn.clicked.connect(self.on_reporting_btn_clicked)  # noqa

        # unique chart saving
        self.unique_chart_save_label = QLabel()
        self.unique_chart_save_label.setText('Save Unique Charts:')
        self.unique_chart_save_label.setStyleSheet(self.palette.INPUT_LABEL_STYLESHEET)

        self.unique_chart_save_btn = QPushButton()
        self.unique_chart_save_btn.setCheckable(True)
        self.unique_chart_save_btn.setText('OFF')
        self.unique_chart_save_btn.setStyleSheet(self.palette.TOGGLE_BTN_DISABLED_STYLESHEET)
        self.unique_chart_save_btn.clicked.connect(self.on_chart_saving_btn_clicked)  # noqa

        # show results label
        self.show_results_label = QLabel()
        self.show_results_label.setText('Show Results:')
        self.show_results_label.setStyleSheet(self.palette.INPUT_LABEL_STYLESHEET)
        # show results button
        self.show_sim_results_btn = QPushButton()
        self.show_sim_results_btn.setCheckable(True)
        self.show_sim_results_btn.setText('ON')
        self.show_sim_results_btn.setStyleSheet(self.palette.TOGGLE_BTN_ENABLED_STYLESHEET)
        self.show_sim_results_btn.clicked.connect(self.on_show_results_btn_clicked)  # noqa

        # results depth label
        self.results_depth_label = QLabel()
        self.results_depth_label.setText('Results Depth:')
        self.results_depth_label.setStyleSheet(self.palette.INPUT_LABEL_STYLESHEET)
        # results depth radio button
        self.data_and_charts_radio_btn = QRadioButton("Data and Charts")
        self.data_and_charts_radio_btn.toggled.connect(self.data_and_charts_btn_selected)  # noqa
        self.data_and_charts_radio_btn.setStyleSheet(self.palette.RADIO_BTN_STYLESHEET)
        self.data_and_charts_radio_btn.toggle()  # set data and charts as default
        # results depth radio button
        self.data_only_radio_btn = QRadioButton("Data Only")
        self.data_only_radio_btn.toggled.connect(self.data_only_btn_selected)  # noqa
        self.data_only_radio_btn.setStyleSheet(self.palette.RADIO_BTN_STYLESHEET)

        # run button
        self.run_btn = QPushButton()
        self.run_btn.setFixedSize(60, 30)
        self.run_btn.setText('RUN')
        self.run_btn.clicked.connect(self.on_run_btn_clicked)  # noqa
        self.run_btn.setStyleSheet(self.palette.RUN_BTN_STYLESHEET)

        # error message box
        self.error_message_box = QLabel()
        self.error_message_box.setStyleSheet(self.palette.ERROR_LABEL_STYLESHEET)

    def on_strategy_studio_btn_clicked(self, filepath):
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

    def on_logging_btn_clicked(self):
        if self.logging_btn.isChecked():
            self.simulation_logging = True
            self.logging_btn.setText('ON')
            self.logging_btn.setStyleSheet(Palette.TOGGLE_BTN_ENABLED_STYLESHEET)
        else:
            self.simulation_logging = False
            self.logging_btn.setText('OFF')
            self.logging_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)

    def on_reporting_btn_clicked(self):
        if self.reporting_btn.isChecked():
            self.simulation_reporting = True
            self.reporting_btn.setText('ON')
            self.reporting_btn.setStyleSheet(Palette.TOGGLE_BTN_ENABLED_STYLESHEET)
        else:
            self.simulation_reporting = False
            self.reporting_btn.setText('OFF')
            self.reporting_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)

    def on_chart_saving_btn_clicked(self):
        if self.unique_chart_save_btn.isChecked():
            self.simulation_unique_chart_saving = True
            self.unique_chart_save_btn.setText('ON')
            self.unique_chart_save_btn.setStyleSheet(Palette.TOGGLE_BTN_ENABLED_STYLESHEET)
        else:
            self.simulation_unique_chart_saving = False
            self.unique_chart_save_btn.setText('OFF')
            self.unique_chart_save_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)

    def on_show_results_btn_clicked(self):
        if self.show_sim_results_btn.isChecked():
            self.simulation_show_results_window = True
            self.show_sim_results_btn.setText('ON')
            self.show_sim_results_btn.setStyleSheet(Palette.TOGGLE_BTN_ENABLED_STYLESHEET)
        else:
            self.simulation_show_results_window = False
            self.show_sim_results_btn.setText('OFF')
            self.show_sim_results_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)

    def data_and_charts_btn_selected(self, selected):
        if selected:
            self.results_depth = Simulator.CHARTS_AND_DATA

    def data_only_btn_selected(self, selected):
        if selected:
            self.results_depth = Simulator.DATA_ONLY

    def load_strategy(self, filepath, cache_key=None, cache_value=None):
        if filepath is None or filepath == '':
            self.error_message_box.setText('You must select a strategy file!')
            return None
        try:
            with open(filepath, 'r') as file:
                strategy = json.load(file)
        except FileNotFoundError:
            self.error_message_box.setText('Strategy file not found!')
            return None
        except Exception as e:
            self.error_message_box.setText(f'Uncaught error parsing strategy file: {e}')
            return None

        # cache the strategy filepath (create if it does not already exist)
        self.cache_strategy_filepath(filepath, cache_key, cache_value)

        # inject the unix equivalent dates from the combobox to the dict
        strategy['strategy_filepath'] = filepath
        strategy['start'] = int(time.time()) - self.simulation_length
        strategy['end'] = int(time.time())

        return strategy

    def cache_strategy_filepath(self, strategy_filepath, cache_key=None, cache_value=None):
        # cache the strategy filepath (create if it does not already exist)

        key = self.DEFAULT_CACHE_KEY
        if cache_key:
            key = cache_key

        # get the existing cache data
        with open(self.CACHE_FILE_FILEPATH, 'r') as file:
            data = json.load(file)

        # add the filepath to the cache data
        if cache_value:
            data[key] = cache_value
        else:
            data[key] = strategy_filepath

        # write the cache data
        with open(self.CACHE_FILE_FILEPATH, 'w+') as file:
            json.dump(data, file)

    @abstractmethod
    def on_run_btn_clicked(self):
        raise NotImplementedError('You need to implement this method!')
