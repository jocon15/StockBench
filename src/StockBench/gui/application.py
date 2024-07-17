import os
import json

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QPushButton, QLineEdit
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import Qt
from PyQt6 import QtGui

from StockBench.gui.windows.base.base.config_tab import ConfigTab
from StockBench.gui.windows.singular.singular_results_window import SingularResultsWindow
from StockBench.gui.windows.multi.multi_results_window import MultiResultsWindow
from StockBench.gui.palette.palette import Palette
from StockBench.gui.windows.head_to_head.head_to_head_window import HeadToHeadWindow
from StockBench.gui.windows.folder.folder_results_window import FolderResultsWindow


class ConfigMainWindow(QMainWindow):
    WIDTH = 400
    HEIGHT = 750

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
        self.tab_widget.addTab(HeadToHeadConfigTab(), "Compare")
        self.tab_widget.addTab(FolderConfigTab(), "Folder")
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
        # add components to the layout
        label = QLabel()
        label.setText('Strategy:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.strategy_selection_box = StrategySelection()
        self.strategy_selection_box.setStyleSheet(Palette.SELECT_FILE_BTN_STYLESHEET)
        self.layout.addWidget(self.strategy_selection_box)

        self.strategy_studio_btn = QPushButton()
        self.strategy_studio_btn.setText('Strategy Studio (beta)')
        self.strategy_studio_btn.clicked.connect(lambda: self.on_strategy_studio_btn_clicked(  # noqa
                                                 self.strategy_selection_box.filepath_box.text()))
        self.strategy_studio_btn.setStyleSheet(Palette.SELECT_FILE_BTN_STYLESHEET)
        self.layout.addWidget(self.strategy_studio_btn)

        self.layout.addWidget(self.simulation_length_label)

        self.layout.addWidget(self.simulation_length_cbox)

        label = QLabel()
        label.setText('Simulation Symbol:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.symbol_tbox = QLineEdit()
        self.symbol_tbox.setText("MSFT")
        self.symbol_tbox.setStyleSheet(Palette.LINE_EDIT_STYLESHEET)
        self.layout.addWidget(self.symbol_tbox)

        self.layout.addWidget(self.initial_balance_label)

        self.layout.addWidget(self.initial_balance_tbox)

        self.layout.addWidget(self.logging_label)

        self.layout.addWidget(self.logging_btn)

        self.layout.addWidget(self.reporting_label)

        self.layout.addWidget(self.reporting_btn)

        label = QLabel()
        label.setText('Save Unique Chart:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.unique_chart_save_btn = QPushButton()
        self.unique_chart_save_btn.setCheckable(True)
        self.unique_chart_save_btn.setText('OFF')
        self.unique_chart_save_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)
        self.unique_chart_save_btn.clicked.connect(self.on_chart_saving_btn_clicked)  # noqa
        self.layout.addWidget(self.unique_chart_save_btn)

        self.layout.addWidget(self.show_results_label)

        self.layout.addWidget(self.show_sim_results_btn)

        self.layout.addWidget(self.results_depth_label)

        self.layout.addWidget(self.data_and_charts_radio_btn)

        self.layout.addWidget(self.data_only_radio_btn)

        self.layout.addWidget(self.run_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.layout.addWidget(self.error_message_box)

        self.setLayout(self.layout)

    def on_chart_saving_btn_clicked(self):
        if self.unique_chart_save_btn.isChecked():
            self.simulation_unique_chart_saving = True
            self.unique_chart_save_btn.setText('ON')
            self.unique_chart_save_btn.setStyleSheet(Palette.TOGGLE_BTN_ENABLED_STYLESHEET)
        else:
            self.simulation_unique_chart_saving = False
            self.unique_chart_save_btn.setText('OFF')
            self.unique_chart_save_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)

    def on_run_btn_clicked(self):
        # load the strategy from the JSON file into a strategy python dict
        strategy = self.load_strategy(self.strategy_selection_box.filepath_box.text())

        if strategy is None:
            # strategy load failed
            return

        # gather other data from UI components
        simulation_symbol = self.symbol_tbox.text().upper().strip()
        simulation_balance = float(self.initial_balance_tbox.text())

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
        # add components to the layout
        label = QLabel()
        label.setText('Strategy:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.strategy_selection_box = StrategySelection()
        self.strategy_selection_box.setStyleSheet(Palette.SELECT_FILE_BTN_STYLESHEET)
        self.layout.addWidget(self.strategy_selection_box)

        self.strategy_studio_btn = QPushButton()
        self.strategy_studio_btn.setText('Strategy Studio (beta)')
        self.strategy_studio_btn.clicked.connect(lambda: self.on_strategy_studio_btn_clicked(  # noqa
                                                 self.strategy_selection_box.filepath_box.text()))
        self.strategy_studio_btn.setStyleSheet(Palette.SELECT_FILE_BTN_STYLESHEET)
        self.layout.addWidget(self.strategy_studio_btn)

        self.layout.addWidget(self.simulation_length_label)

        self.layout.addWidget(self.simulation_length_cbox)

        label = QLabel()
        label.setText('Simulation Symbols:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.symbol_tbox = QLineEdit()
        self.symbol_tbox.setText("MSFT, AAPL")
        self.symbol_tbox.setStyleSheet(Palette.LINE_EDIT_STYLESHEET)
        self.layout.addWidget(self.symbol_tbox)

        self.layout.addWidget(self.initial_balance_label)

        self.layout.addWidget(self.initial_balance_tbox)

        self.layout.addWidget(self.logging_label)

        self.layout.addWidget(self.logging_btn)

        self.layout.addWidget(self.reporting_label)

        self.layout.addWidget(self.reporting_btn)

        label = QLabel()
        label.setText('Save Unique Charts:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.unique_chart_save_btn = QPushButton()
        self.unique_chart_save_btn.setCheckable(True)
        self.unique_chart_save_btn.setText('OFF')
        self.unique_chart_save_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)
        self.unique_chart_save_btn.clicked.connect(self.on_chart_saving_btn_clicked)  # noqa
        self.layout.addWidget(self.unique_chart_save_btn)

        self.layout.addWidget(self.show_results_label)

        self.layout.addWidget(self.show_sim_results_btn)

        self.layout.addWidget(self.results_depth_label)

        self.layout.addWidget(self.data_and_charts_radio_btn)

        self.layout.addWidget(self.data_only_radio_btn)

        self.layout.addWidget(self.run_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.layout.addWidget(self.error_message_box)

        self.setLayout(self.layout)

    def on_chart_saving_btn_clicked(self):
        if self.unique_chart_save_btn.isChecked():
            self.simulation_unique_chart_saving = True
            self.unique_chart_save_btn.setText('ON')
            self.unique_chart_save_btn.setStyleSheet(Palette.TOGGLE_BTN_ENABLED_STYLESHEET)
        else:
            self.simulation_unique_chart_saving = False
            self.unique_chart_save_btn.setText('OFF')
            self.unique_chart_save_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)

    def on_run_btn_clicked(self):
        # load the strategy from the JSON file into a strategy python dict
        strategy = self.load_strategy(self.strategy_selection_box.filepath_box.text())

        if strategy is None:
            # strategy load failed
            return

        # gather other data from UI components
        raw_simulation_symbols = self.symbol_tbox.text().split(',')
        simulation_symbols = []
        for symbol in raw_simulation_symbols:
            simulation_symbols.append(symbol.upper().strip())
        simulation_balance = float(self.initial_balance_tbox.text())

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


class HeadToHeadConfigTab(ConfigTab):
    STRATEGY_1_CACHE_KEY = 'cached_h2h_strategy_1_filepath'

    STRATEGY_2_CACHE_KEY = 'cached_h2h_strategy_2_filepath'

    def __init__(self):
        super().__init__()
        # add components to the layout
        label = QLabel()
        label.setText('Strategy 1:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.strategy_1_selection_box = StrategySelection(self.STRATEGY_1_CACHE_KEY)
        self.strategy_1_selection_box.setStyleSheet(Palette.SELECT_FILE_BTN_STYLESHEET)
        self.layout.addWidget(self.strategy_1_selection_box)

        self.strategy_1_studio_btn = QPushButton()
        self.strategy_1_studio_btn.setText('Strategy Studio (beta)')
        self.strategy_1_studio_btn.clicked.connect(lambda: self.on_strategy_studio_btn_clicked(  # noqa
                                                   self.strategy_1_selection_box.filepath_box.text()))
        self.strategy_1_studio_btn.setStyleSheet(Palette.SELECT_FILE_BTN_STYLESHEET)
        self.layout.addWidget(self.strategy_1_studio_btn)

        label = QLabel()
        label.setText('Strategy 2:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.strategy_2_selection_box = StrategySelection(self.STRATEGY_2_CACHE_KEY)
        self.strategy_2_selection_box.setStyleSheet(Palette.SELECT_FILE_BTN_STYLESHEET)
        self.layout.addWidget(self.strategy_2_selection_box)

        self.strategy_2_studio_btn = QPushButton()
        self.strategy_2_studio_btn.setText('Strategy Studio (beta)')
        self.strategy_2_studio_btn.clicked.connect(lambda: self.on_strategy_studio_btn_clicked(  # noqa
                                                   self.strategy_2_selection_box.filepath_box.text()))
        self.strategy_2_studio_btn.setStyleSheet(Palette.SELECT_FILE_BTN_STYLESHEET)
        self.layout.addWidget(self.strategy_2_studio_btn)

        self.layout.addWidget(self.simulation_length_label)

        self.layout.addWidget(self.simulation_length_cbox)

        label = QLabel()
        label.setText('Simulation Symbols:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.symbol_tbox = QLineEdit()
        self.symbol_tbox.setText("MSFT, AAPL")
        self.symbol_tbox.setStyleSheet(Palette.LINE_EDIT_STYLESHEET)
        self.layout.addWidget(self.symbol_tbox)

        self.layout.addWidget(self.initial_balance_label)

        self.layout.addWidget(self.initial_balance_tbox)

        self.layout.addWidget(self.logging_label)

        self.layout.addWidget(self.logging_btn)

        self.layout.addWidget(self.reporting_label)

        self.layout.addWidget(self.reporting_btn)

        self.layout.addWidget(self.show_results_label)

        self.layout.addWidget(self.show_sim_results_btn)

        self.layout.addWidget(self.results_depth_label)

        self.layout.addWidget(self.data_and_charts_radio_btn)

        self.layout.addWidget(self.data_only_radio_btn)

        self.layout.addWidget(self.run_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.layout.addWidget(self.error_message_box)

        # add the layout to the widget
        self.setLayout(self.layout)

    def on_run_btn_clicked(self):
        # load the strategy from the JSON file into a strategy python dict
        strategy1 = self.load_strategy(self.strategy_1_selection_box.filepath_box.text(), self.STRATEGY_1_CACHE_KEY)
        strategy2 = self.load_strategy(self.strategy_2_selection_box.filepath_box.text(), self.STRATEGY_2_CACHE_KEY)

        if strategy1 is None or strategy2 is None:
            # FIXME: put error message here?
            # either strategy load failed
            return

        # gather other data from UI components
        raw_simulation_symbols = self.symbol_tbox.text().split(',')
        simulation_symbols = []
        for symbol in raw_simulation_symbols:
            simulation_symbols.append(symbol.upper().strip())
        simulation_balance = float(self.initial_balance_tbox.text())

        # check the balance for negative numbers
        if simulation_balance <= 0:
            self.error_message_box.setText('Initial account balance must be a positive number!')
            return

        # reminder: h2h will store the references of these simulations, so we do not need to attribute them with self
        # also, h2h will call the begin functions

        # create simulation number 1
        simulation_result_window_1 = MultiResultsWindow(
            simulation_symbols,
            strategy1,
            simulation_balance,
            self.simulator,
            self.progress_bar_observer,
            self.worker,
            self.simulation_logging,
            self.simulation_reporting,
            self.simulation_unique_chart_saving,
            self.results_depth)

        # create simulation number 2
        simulation_result_window_2 = MultiResultsWindow(
            simulation_symbols,
            strategy2,
            simulation_balance,
            self.simulator,
            self.progress_bar_observer,
            self.worker,
            self.simulation_logging,
            self.simulation_reporting,
            True,  # prevent the second chart from loading the temp chart (being used by sim 1)
            self.results_depth)

        # create the h2h window - passing the simulations into the constructor
        self.head_to_head_window = HeadToHeadWindow(simulation_result_window_1, simulation_result_window_2)

        if self.simulation_show_results_window:
            # show the results window if option is checked
            self.head_to_head_window.showMaximized()


class FolderConfigTab(ConfigTab):
    FOLDER_CACHE_KEY = 'cached_folderpath'

    def __init__(self):
        super().__init__()
        # add components to the layout
        label = QLabel()
        label.setText('Folder:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.folder_selection = FolderSelection()
        self.folder_selection.setStyleSheet(Palette.SELECT_FILE_BTN_STYLESHEET)
        self.layout.addWidget(self.folder_selection)

        self.layout.addWidget(self.simulation_length_label)

        self.layout.addWidget(self.simulation_length_cbox)

        label = QLabel()
        label.setText('Simulation Symbols:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.symbol_tbox = QLineEdit()
        self.symbol_tbox.setText("MSFT, AAPL")
        self.symbol_tbox.setStyleSheet(Palette.LINE_EDIT_STYLESHEET)
        self.layout.addWidget(self.symbol_tbox)

        self.layout.addWidget(self.initial_balance_label)

        self.layout.addWidget(self.initial_balance_tbox)

        self.layout.addWidget(self.logging_label)

        self.layout.addWidget(self.logging_btn)

        label = QLabel()
        label.setText('Save Unique Charts:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.unique_chart_save_btn = QPushButton()
        self.unique_chart_save_btn.setCheckable(True)
        self.unique_chart_save_btn.setText('OFF')
        self.unique_chart_save_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)
        self.unique_chart_save_btn.clicked.connect(self.on_chart_saving_btn_clicked)  # noqa
        self.layout.addWidget(self.unique_chart_save_btn)

        self.layout.addWidget(self.show_results_label)

        self.layout.addWidget(self.show_sim_results_btn)

        self.layout.addWidget(self.run_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.layout.addWidget(self.error_message_box)

        self.setLayout(self.layout)

    def on_run_btn_clicked(self):
        # extract the folder path from the input
        folderpath = self.folder_selection.folderpath_box.text()

        # gather other data from UI components
        raw_simulation_symbols = self.symbol_tbox.text().split(',')
        simulation_symbols = []
        for symbol in raw_simulation_symbols:
            simulation_symbols.append(symbol.upper().strip())
        simulation_balance = float(self.initial_balance_tbox.text())

        # check the balance for negative numbers
        if simulation_balance <= 0:
            self.error_message_box.setText('Initial account balance must be a positive number!')
            return

        # create a list of simulations
        strategies = []

        # iterate through all files in the folder, loading the strategies into a list
        for filename in os.listdir(folderpath):
            filepath = os.path.join(folderpath, filename)

            strategy = self.load_strategy(filepath, self.FOLDER_CACHE_KEY, folderpath)

            strategies.append(strategy)

        # create a new simulations results window
        self.simulation_result_window = FolderResultsWindow(
            strategies,
            simulation_symbols,
            simulation_balance,
            self.simulator,
            self.progress_bar_observer,
            self.worker,
            self.simulation_logging,
            self.simulation_reporting,
            self.simulation_unique_chart_saving,
            None)

        # all error checks have passed, can now clear the error message box
        self.error_message_box.setText('')

        # begin the simulation and progress checking timer
        self.simulation_result_window.begin()

        if self.simulation_show_results_window:
            # show the results window if option is checked
            self.simulation_result_window.showMaximized()

    def on_chart_saving_btn_clicked(self):
        if self.unique_chart_save_btn.isChecked():
            self.simulation_unique_chart_saving = True
            self.unique_chart_save_btn.setText('ON')
            self.unique_chart_save_btn.setStyleSheet(Palette.TOGGLE_BTN_ENABLED_STYLESHEET)
        else:
            self.simulation_unique_chart_saving = False
            self.unique_chart_save_btn.setText('OFF')
            self.unique_chart_save_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)


class StrategySelection(QWidget):
    FILEPATH_BOX_STYLESHEET = """background-color: #303134;color: #FFF;"""

    SELECT_FILE_BTN_STYLESHEET = """background-color: #303134;color: #FFF;"""

    CACHE_FILE_FILEPATH = 'cache.json'

    DEFAULT_CACHE_KEY = 'cached_strategy_filepath'

    def __init__(self, cache_key=None):
        super().__init__()

        self.layout = QHBoxLayout()

        self.filepath_box = QLabel()
        self.filepath_box.setStyleSheet(self.FILEPATH_BOX_STYLESHEET)
        self.layout.addWidget(self.filepath_box)
        self.apply_cached_strategy_filepath(cache_key)

        self.select_file_btn = QPushButton()
        self.select_file_btn.setText('Select File')
        self.select_file_btn.clicked.connect(self.on_select_file_btn_clicked)  # noqa
        self.select_file_btn.setStyleSheet(self.SELECT_FILE_BTN_STYLESHEET)
        self.layout.addWidget(self.select_file_btn)

        self.setLayout(self.layout)

    def apply_cached_strategy_filepath(self, cache_key=None):
        if os.path.exists(self.CACHE_FILE_FILEPATH):
            with open(self.CACHE_FILE_FILEPATH, 'r') as file:
                data = json.load(file)

            # swap the key to the passed key if one was entered (used when using h2h cached keys)
            key = self.DEFAULT_CACHE_KEY
            if cache_key:
                key = cache_key

            if key in data.keys():
                self.filepath_box.setText(data[key])

    def on_select_file_btn_clicked(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dlg.setNameFilter("JSON (*.json)")
        if dlg.exec():
            filenames = dlg.selectedFiles()
            self.filepath_box.setText(filenames[0])


class FolderSelection(QWidget):
    FILEPATH_BOX_STYLESHEET = """background-color: #303134;color: #FFF;"""

    SELECT_FILE_BTN_STYLESHEET = """background-color: #303134;color: #FFF;"""

    CACHE_FILE_FILEPATH = 'cache.json'

    DEFAULT_CACHE_KEY = 'cached_folderpath'

    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()

        self.folderpath_box = QLabel()
        self.folderpath_box.setStyleSheet(self.FILEPATH_BOX_STYLESHEET)
        self.layout.addWidget(self.folderpath_box)
        self.apply_cached_folderpath()

        self.select_folder_btn = QPushButton()
        self.select_folder_btn.setText('Select Folder')
        self.select_folder_btn.clicked.connect(self.on_select_folder_btn_clicked)  # noqa
        self.select_folder_btn.setStyleSheet(self.SELECT_FILE_BTN_STYLESHEET)
        self.layout.addWidget(self.select_folder_btn)

        self.setLayout(self.layout)

    def apply_cached_folderpath(self):
        if os.path.exists(self.CACHE_FILE_FILEPATH):
            with open(self.CACHE_FILE_FILEPATH, 'r') as file:
                data = json.load(file)

            if self.DEFAULT_CACHE_KEY in data.keys():
                self.folderpath_box.setText(data[self.DEFAULT_CACHE_KEY])

    def on_select_folder_btn_clicked(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.Directory)
        dlg.setNameFilter("JSON (*.json)")
        if dlg.exec():
            filenames = dlg.selectedFiles()
            self.folderpath_box.setText(filenames[0])
