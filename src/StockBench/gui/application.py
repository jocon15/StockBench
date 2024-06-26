import os
import json
import time

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QLabel, QPushButton, QComboBox
from PyQt6.QtWidgets import QFileDialog, QLineEdit, QRadioButton
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QDoubleValidator
from PyQt6 import QtGui

from StockBench.gui.windows.base.base.config_tab import ConfigTab
from StockBench.gui.windows.singular.singular_results_window import SingularResultsWindow
from StockBench.gui.windows.multi.multi_results_window import MultiResultsWindow
from StockBench.constants import *
from StockBench.gui.windows.strategy_studio import StrategyStudioWindow
from StockBench.gui.palette.palette import Palette
from StockBench.simulator import Simulator


class ConfigMainWindow(QMainWindow):
    WIDTH = 400
    HEIGHT = 650

    def __init__(self, splash):
        super().__init__()
        self.splash = splash

        # main window styling (do it first to prevent window shifting)
        self.setWindowIcon(QtGui.QIcon(os.path.join('resources', 'images', 'candle.ico')))
        self.setWindowTitle('Configuration')
        # set window geometry
        self.__set_geometry()

        self.layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(SingularConfigTab(), "Single")
        self.tab_widget.addTab(MultiConfigTab(), "Multi")
        self.tab_widget.setStyleSheet(Palette.TAB_WIDGET_STYLESHEET)
        self.layout.addWidget(self.tab_widget)

        widget = QWidget()
        widget.setStyleSheet(Palette.WINDOW_STYLESHEET)
        widget.setLayout(self.layout)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)

        # close the splash window
        self.splash.close()

    def __set_geometry(self):
        self.setFixedSize(self.WIDTH, self.HEIGHT)


class SingularConfigTab(ConfigTab):
    def __init__(self):
        super().__init__()
        # layout type
        self.layout = QVBoxLayout()

        label = QLabel()
        label.setText('Strategy:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.strategy_selection_box = StrategySelection()
        self.strategy_selection_box.setStyleSheet(Palette.SELECT_FILE_BTN_STYLESHEET)
        self.layout.addWidget(self.strategy_selection_box)
        self.strategy_studio_btn = QPushButton()
        self.strategy_studio_btn.setText('Strategy Studio (beta)')
        self.strategy_studio_btn.clicked.connect(self.on_strategy_studio_btn_clicked)  # noqa
        self.strategy_studio_btn.setStyleSheet(Palette.SELECT_FILE_BTN_STYLESHEET)
        self.layout.addWidget(self.strategy_studio_btn)

        label = QLabel()
        label.setText('Simulation Length:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.simulation_length_cbox = QComboBox()
        self.simulation_length_cbox.addItem('1 Year')
        self.simulation_length_cbox.addItem('2 Year')
        self.simulation_length_cbox.addItem('5 Year')
        # set simulation length default to 2 years (must set attribute as well)
        self.simulation_length_cbox.setCurrentIndex(1)
        self.simulation_length = SECONDS_2_YEAR

        self.simulation_length_cbox.setStyleSheet(Palette.COMBOBOX_STYLESHEET)
        self.simulation_length_cbox.currentIndexChanged.connect(self.on_simulation_length_cbox_index_changed)  # noqa
        self.layout.addWidget(self.simulation_length_cbox)

        label = QLabel()
        label.setText('Simulation Symbol:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.symbol_tbox = QLineEdit()
        self.symbol_tbox.setText("MSFT")
        self.symbol_tbox.setStyleSheet(Palette.LINE_EDIT_STYLESHEET)
        self.layout.addWidget(self.symbol_tbox)

        label = QLabel()
        label.setText('Initial Balance:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.balance_tbox = QLineEdit()
        self.balance_tbox.setText('1000.0')
        self.onlyFloat = QDoubleValidator()
        self.balance_tbox.setValidator(self.onlyFloat)
        self.balance_tbox.setStyleSheet(Palette.LINE_EDIT_STYLESHEET)
        self.layout.addWidget(self.balance_tbox)

        label = QLabel()
        label.setText('Logging:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.logging_btn = QPushButton()
        self.logging_btn.setCheckable(True)
        self.logging_btn.setText('OFF')
        self.logging_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)
        self.logging_btn.clicked.connect(self.on_logging_btn_clicked)  # noqa
        self.layout.addWidget(self.logging_btn)

        label = QLabel()
        label.setText('Reporting:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.reporting_btn = QPushButton()
        self.reporting_btn.setCheckable(True)
        self.reporting_btn.setText('OFF')
        self.reporting_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)
        self.reporting_btn.clicked.connect(self.on_reporting_btn_clicked)  # noqa
        self.layout.addWidget(self.reporting_btn)

        label = QLabel()
        label.setText('Save Unique Chart:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.unique_chart_save_btn = QPushButton()
        self.unique_chart_save_btn.setCheckable(True)
        self.unique_chart_save_btn.setText('OFF')
        self.unique_chart_save_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)
        self.unique_chart_save_btn.clicked.connect(self.on_chart_saving_btn_clicked)  # noqa
        self.layout.addWidget(self.unique_chart_save_btn)

        label = QLabel()
        label.setText('Show Results:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.show_sim_results_btn = QPushButton()
        self.show_sim_results_btn.setCheckable(True)
        self.show_sim_results_btn.setText('ON')
        self.show_sim_results_btn.setStyleSheet(Palette.TOGGLE_BTN_ENABLED_STYLESHEET)
        self.show_sim_results_btn.clicked.connect(self.on_show_results_btn_clicked)  # noqa
        self.layout.addWidget(self.show_sim_results_btn)

        label = QLabel()
        label.setText('Results Depth:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.data_and_charts_radio_btn = QRadioButton("Data and Charts")
        self.data_and_charts_radio_btn.toggled.connect(self.data_and_charts_btn_selected)  # noqa
        self.data_and_charts_radio_btn.setStyleSheet(Palette.RADIO_BTN_STYLESHEET)
        self.data_and_charts_radio_btn.toggle()  # set data and charts as default
        self.layout.addWidget(self.data_and_charts_radio_btn)
        self.data_only_radio_btn = QRadioButton("Data Only")
        self.data_only_radio_btn.toggled.connect(self.data_only_btn_selected)  # noqa
        self.layout.addWidget(self.data_only_radio_btn)
        self.data_only_radio_btn.setStyleSheet(Palette.RADIO_BTN_STYLESHEET)

        self.run_btn = QPushButton()
        self.run_btn.setFixedSize(60, 30)
        self.run_btn.setText('RUN')
        self.run_btn.clicked.connect(self.on_run_btn_clicked)  # noqa
        self.run_btn.setStyleSheet(Palette.RUN_BTN_STYLESHEET)
        self.layout.addWidget(self.run_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.error_message_box = QLabel()
        self.error_message_box.setStyleSheet(Palette.ERROR_LABEL_STYLESHEET)
        self.layout.addWidget(self.error_message_box)

        self.setLayout(self.layout)

        # render the window
        self.show()

    def on_strategy_studio_btn_clicked(self):
        # launch the strategy studio window injecting the filepath from the filepath box into the strategy editor
        coordinates = self.mapToGlobal(QPoint(0, 0))
        self.strategy_studio_window = StrategyStudioWindow(
            self.strategy_selection_box.filepath_box.text(),
            coordinates,
            self.width()
        )
        self.strategy_studio_window.show()

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

    def on_simulation_length_cbox_index_changed(self, index):
        if index == 0:
            self.simulation_length = SECONDS_1_YEAR
        elif index == 1:
            self.simulation_length = SECONDS_2_YEAR
        elif index == 2:
            self.simulation_length = SECONDS_5_YEAR

    def data_and_charts_btn_selected(self, selected):
        if selected:
            self.results_depth = Simulator.CHARTS_AND_DATA

    def data_only_btn_selected(self, selected):
        if selected:
            self.results_depth = Simulator.DATA_ONLY

    def on_run_btn_clicked(self):
        # load the strategy from the JSON file into a strategy python dict

        strategy_filepath = self.strategy_selection_box.filepath_box.text()

        if strategy_filepath is None or strategy_filepath == '':
            self.error_message_box.setText('You must select a strategy file!')
            return
        try:
            with open(strategy_filepath, 'r') as file:
                strategy = json.load(file)
        except FileNotFoundError:
            self.error_message_box.setText('Strategy file not found!')
            return
        except Exception as e:
            self.error_message_box.setText(f'Uncaught error parsing strategy file: {e}')
            return

        # cache the strategy filepath (create if it does not already exist)
        self.cache_strategy_filepath(strategy_filepath)

        # inject the unix equivalent dates from the combobox to the dict
        strategy['strategy_filepath'] = strategy_filepath
        strategy['start'] = int(time.time()) - self.simulation_length
        strategy['end'] = int(time.time())

        # gather other data from UI components
        simulation_symbol = self.symbol_tbox.text().upper().strip()
        simulation_balance = float(self.balance_tbox.text())

        if simulation_balance <= 0:
            self.error_message_box.setText('Initial account balance must be a positive number!')
            return

        # create a new simulations results window
        self.simulation_result_window = SingularResultsWindow(
            simulation_symbol,
            strategy,
            simulation_balance,
            self.simulator,
            self.progress_bar_observer,
            self.worker,
            self.simulation_logging,
            self.simulation_reporting,
            self.simulation_unique_chart_saving,
            self.results_depth)

        # all error checks have passed, can now clear the error message box
        self.error_message_box.setText('')

        # begin the simulation and progress checking timer
        self.simulation_result_window.begin()

        if self.simulation_show_results_window:
            # show the results window if option is checked
            self.simulation_result_window.showMaximized()


class MultiConfigTab(ConfigTab):
    def __init__(self):
        super().__init__()
        # layout type
        self.layout = QVBoxLayout()

        label = QLabel()
        label.setText('Strategy:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.strategy_selection_box = StrategySelection()
        self.strategy_selection_box.setStyleSheet(Palette.SELECT_FILE_BTN_STYLESHEET)
        self.layout.addWidget(self.strategy_selection_box)
        self.strategy_studio_btn = QPushButton()
        self.strategy_studio_btn.setText('Strategy Studio (beta)')
        self.strategy_studio_btn.clicked.connect(self.on_strategy_studio_btn_clicked)  # noqa
        self.strategy_studio_btn.setStyleSheet(Palette.SELECT_FILE_BTN_STYLESHEET)
        self.layout.addWidget(self.strategy_studio_btn)

        label = QLabel()
        label.setText('Simulation Length:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.simulation_length_cbox = QComboBox()
        self.simulation_length_cbox.addItem('1 Year')
        self.simulation_length_cbox.addItem('2 Year')
        self.simulation_length_cbox.addItem('5 Year')
        # set simulation length default to 2 years (must set attribute as well)
        self.simulation_length_cbox.setCurrentIndex(1)
        self.simulation_length = SECONDS_2_YEAR

        self.simulation_length_cbox.setStyleSheet(Palette.COMBOBOX_STYLESHEET)
        self.simulation_length_cbox.currentIndexChanged.connect(self.on_simulation_length_cbox_index_changed)  # noqa
        self.layout.addWidget(self.simulation_length_cbox)

        label = QLabel()
        label.setText('Simulation Symbols:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.symbol_tbox = QLineEdit()
        self.symbol_tbox.setText("MSFT, AAPL")
        self.symbol_tbox.setStyleSheet(Palette.LINE_EDIT_STYLESHEET)
        self.layout.addWidget(self.symbol_tbox)

        label = QLabel()
        label.setText('Initial Balance:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.balance_tbox = QLineEdit()
        self.balance_tbox.setText('1000.0')
        self.onlyFloat = QDoubleValidator()
        self.balance_tbox.setValidator(self.onlyFloat)
        self.balance_tbox.setStyleSheet(Palette.LINE_EDIT_STYLESHEET)
        self.layout.addWidget(self.balance_tbox)

        label = QLabel()
        label.setText('Logging:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.logging_btn = QPushButton()
        self.logging_btn.setCheckable(True)
        self.logging_btn.setText('OFF')
        self.logging_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)
        self.logging_btn.clicked.connect(self.on_logging_btn_clicked)  # noqa
        self.layout.addWidget(self.logging_btn)

        label = QLabel()
        label.setText('Reporting:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.reporting_btn = QPushButton()
        self.reporting_btn.setCheckable(True)
        self.reporting_btn.setText('OFF')
        self.reporting_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)
        self.reporting_btn.clicked.connect(self.on_reporting_btn_clicked)  # noqa
        self.layout.addWidget(self.reporting_btn)

        label = QLabel()
        label.setText('Save Unique Charts:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.unique_chart_save_btn = QPushButton()
        self.unique_chart_save_btn.setCheckable(True)
        self.unique_chart_save_btn.setText('OFF')
        self.unique_chart_save_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)
        self.unique_chart_save_btn.clicked.connect(self.on_chart_saving_btn_clicked)  # noqa
        self.layout.addWidget(self.unique_chart_save_btn)

        label = QLabel()
        label.setText('Show Results:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.show_sim_results_btn = QPushButton()
        self.show_sim_results_btn.setCheckable(True)
        self.show_sim_results_btn.setText('ON')
        self.show_sim_results_btn.setStyleSheet(Palette.TOGGLE_BTN_ENABLED_STYLESHEET)
        self.show_sim_results_btn.clicked.connect(self.on_show_results_btn_clicked)  # noqa
        self.layout.addWidget(self.show_sim_results_btn)

        label = QLabel()
        label.setText('Results Depth:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.data_and_charts_radio_btn = QRadioButton("Data and Charts")
        self.data_and_charts_radio_btn.toggled.connect(self.data_and_charts_btn_selected)  # noqa
        self.data_and_charts_radio_btn.setStyleSheet(Palette.RADIO_BTN_STYLESHEET)
        self.data_and_charts_radio_btn.toggle()  # set data and charts as default
        self.layout.addWidget(self.data_and_charts_radio_btn)
        self.data_only_radio_btn = QRadioButton("Data Only")
        self.data_only_radio_btn.toggled.connect(self.data_only_btn_selected)  # noqa
        self.layout.addWidget(self.data_only_radio_btn)
        self.data_only_radio_btn.setStyleSheet(Palette.RADIO_BTN_STYLESHEET)

        self.run_btn = QPushButton()
        self.run_btn.setFixedSize(60, 30)
        self.run_btn.setText('RUN')
        self.run_btn.clicked.connect(self.on_run_btn_clicked)  # noqa
        self.run_btn.setStyleSheet(Palette.RUN_BTN_STYLESHEET)
        self.layout.addWidget(self.run_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.error_message_box = QLabel()
        self.error_message_box.setStyleSheet(Palette.ERROR_LABEL_STYLESHEET)
        self.layout.addWidget(self.error_message_box)

        self.setLayout(self.layout)

        # render the window
        self.show()

    def on_strategy_studio_btn_clicked(self):
        # launch the strategy studio window injecting the filepath from the filepath box into the strategy editor
        coordinates = self.mapToGlobal(QPoint(0, 0))
        self.strategy_studio_window = StrategyStudioWindow(
            self.strategy_selection_box.filepath_box.text(),
            coordinates,
            self.width()
        )
        self.strategy_studio_window.show()

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

    def on_simulation_length_cbox_index_changed(self, index):
        if index == 0:
            self.simulation_length = SECONDS_1_YEAR
        elif index == 1:
            self.simulation_length = SECONDS_2_YEAR
        elif index == 2:
            self.simulation_length = SECONDS_5_YEAR

    def data_and_charts_btn_selected(self, selected):
        if selected:
            self.results_depth = Simulator.CHARTS_AND_DATA

    def data_only_btn_selected(self, selected):
        if selected:
            self.results_depth = Simulator.DATA_ONLY

    def on_run_btn_clicked(self):
        # load the strategy from the JSON file into a strategy python dict
        strategy_filepath = self.strategy_selection_box.filepath_box.text()
        if strategy_filepath is None or strategy_filepath == '':
            self.error_message_box.setText('You must select a strategy file!')
            return
        try:
            with open(strategy_filepath, 'r') as file:
                strategy = json.load(file)
        except FileNotFoundError:
            self.error_message_box.setText('Strategy file not found!')
            return
        except Exception as e:
            self.error_message_box.setText(f'Uncaught error parsing strategy file: {e}')
            return

        # cache the strategy filepath (create if it does not already exist)
        self.cache_strategy_filepath(strategy_filepath)

        # inject the unix equivalent dates from the combobox to the dict
        strategy['strategy_filepath'] = strategy_filepath
        strategy['start'] = int(time.time()) - self.simulation_length
        strategy['end'] = int(time.time())

        # gather other data from UI components
        raw_simulation_symbols = self.symbol_tbox.text().split(',')
        simulation_symbols = []
        for symbol in raw_simulation_symbols:
            simulation_symbols.append(symbol.upper().strip())
        simulation_balance = float(self.balance_tbox.text())

        # check the balance for negative numbers
        if simulation_balance <= 0:
            self.error_message_box.setText('Initial account balance must be a positive number!')
            return

        # create a new simulations results window
        self.simulation_result_window = MultiResultsWindow(
            simulation_symbols,
            strategy,
            simulation_balance,
            self.simulator,
            self.progress_bar_observer,
            self.worker,
            self.simulation_logging,
            self.simulation_reporting,
            self.simulation_unique_chart_saving,
            self.results_depth)

        # all error checks have passed, can now clear the error message box
        self.error_message_box.setText('')

        # begin the simulation and progress checking timer
        self.simulation_result_window.begin()

        if self.simulation_show_results_window:
            # show the results window if option is checked
            self.simulation_result_window.showMaximized()


class StrategySelection(QWidget):
    FILEPATH_BOX_STYLESHEET = """background-color: #303134;color: #FFF;"""

    SELECT_FILE_BTN_STYLESHEET = """background-color: #303134;color: #FFF;"""

    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()

        self.filepath_box = QLabel()
        self.filepath_box.setStyleSheet(self.FILEPATH_BOX_STYLESHEET)
        self.layout.addWidget(self.filepath_box)
        self.add_cached_strategy_filepath()

        self.select_file_btn = QPushButton()
        self.select_file_btn.setText('Select File')
        self.select_file_btn.clicked.connect(self.on_select_file_btn_click)  # noqa
        self.select_file_btn.setStyleSheet(self.SELECT_FILE_BTN_STYLESHEET)
        self.layout.addWidget(self.select_file_btn)

        self.setLayout(self.layout)

    def add_cached_strategy_filepath(self):
        filepath = 'cache.json'
        if os.path.exists(filepath):
            with open(filepath, 'r') as file:
                data = json.load(file)
            if 'cached_strategy_filepath' in data.keys():
                self.filepath_box.setText(data['cached_strategy_filepath'])

    def on_select_file_btn_click(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dlg.setNameFilter("JSON (*.json)")
        if dlg.exec():
            filenames = dlg.selectedFiles()
            self.filepath_box.setText(filenames[0])
