import os
import json
import time

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QLabel, QPushButton, QComboBox
from PyQt6.QtWidgets import QFileDialog, QLineEdit
from PyQt6.QtCore import QThreadPool, Qt, QPoint
from PyQt6.QtGui import QDoubleValidator
from PyQt6 import QtGui

from StockBench.gui.worker.worker import Worker
from StockBench.observers.progress_observer import ProgressObserver
from StockBench.simulator import Simulator
from StockBench.gui.windows.singular.singular_results_window import SingularResultsWindow
from StockBench.gui.windows.multi.multi_results_window import MultiResultsWindow
from StockBench.constants import *
from StockBench.gui.windows.strategy_studio import StrategyStudioWindow


class ConfigMainWindow(QMainWindow):
    window_stylesheet = """background-color: #202124;"""
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
        }
    """
    WIDTH = 400
    HEIGHT = 600

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
        self.tab_widget.setStyleSheet(self.tab_widget_stylesheet)
        self.layout.addWidget(self.tab_widget)

        widget = QWidget()
        widget.setStyleSheet(self.window_stylesheet)
        widget.setLayout(self.layout)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)

        # close the splash window
        self.splash.close()

    def __set_geometry(self):
        self.setFixedSize(self.WIDTH, self.HEIGHT)


class SingularConfigTab(QWidget):
    text_box_stylesheet = """background-color: #303134;color:#FFF;border-width:0px;border-radius:10px;height:25px;
        text-indent:3px;"""

    select_file_btn_stylesheet = """background-color: #303134;color:#FFF;border-width:0px;border-radius:10px;
        height:25px;"""

    combobox_stylesheet = """background-color: #303134;color:#FFF;border-width:0px;border-radius:10px;height:25px;
        text-indent:3px;"""

    line_edit_stylesheet = """background-color:#303134;color:#FFF;border-width:0px;border-radius:10px;height:25px;
        text-indent:5px;"""

    toggle_btn_enabled_stylesheet = """background-color:#04ba5f;margin-left:auto;margin-right:auto;
        width:40%;height:25px;border-radius:10px;"""

    toggle_btn_disabled_stylesheet = """background-color: #303134;margin-left: auto;
            margin-right:auto;width: 40%;height:25px;border-radius: 10px;"""

    run_btn_stylesheet = """
            QPushButton
            {
                background-color: #04ba5f;
                color: #FFF;
                border-radius: 10px;
            }
            QPushButton:hover
            {
                background-color: #04ba50;
            }
            """

    error_label_style_sheet = """color:#dc143c;"""

    def __init__(self):
        super().__init__()
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

        self.layout = QVBoxLayout()

        label = QLabel()
        label.setText('Strategy:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.strategy_selection_box = StrategySelection()
        self.strategy_selection_box.setStyleSheet(self.select_file_btn_stylesheet)
        self.layout.addWidget(self.strategy_selection_box)
        self.strategy_studio_btn = QPushButton()
        self.strategy_studio_btn.setText('Strategy Studio (beta)')
        self.strategy_studio_btn.clicked.connect(self.on_strategy_studio_btn_clicked)  # noqa
        self.strategy_studio_btn.setStyleSheet(self.select_file_btn_stylesheet)
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

        self.simulation_length_cbox.setStyleSheet(self.combobox_stylesheet)
        self.simulation_length_cbox.currentIndexChanged.connect(self.on_simulation_length_cbox_index_changed)  # noqa
        self.layout.addWidget(self.simulation_length_cbox)

        label = QLabel()
        label.setText('Simulation Symbol:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.symbol_tbox = QLineEdit()
        self.symbol_tbox.setText("MSFT")
        self.symbol_tbox.setStyleSheet(self.line_edit_stylesheet)
        self.layout.addWidget(self.symbol_tbox)

        label = QLabel()
        label.setText('Initial Balance:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.balance_tbox = QLineEdit()
        self.balance_tbox.setText('1000.0')
        self.onlyFloat = QDoubleValidator()
        self.balance_tbox.setValidator(self.onlyFloat)
        self.balance_tbox.setStyleSheet(self.line_edit_stylesheet)
        self.layout.addWidget(self.balance_tbox)

        label = QLabel()
        label.setText('Logging:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.logging_btn = QPushButton()
        self.logging_btn.setCheckable(True)
        self.logging_btn.setText('OFF')
        self.logging_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)
        self.logging_btn.clicked.connect(self.on_logging_btn_clicked)  # noqa
        self.layout.addWidget(self.logging_btn)

        label = QLabel()
        label.setText('Reporting:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.reporting_btn = QPushButton()
        self.reporting_btn.setCheckable(True)
        self.reporting_btn.setText('OFF')
        self.reporting_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)
        self.reporting_btn.clicked.connect(self.on_reporting_btn_clicked)  # noqa
        self.layout.addWidget(self.reporting_btn)

        label = QLabel()
        label.setText('Save Unique Chart:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.unique_chart_save_btn = QPushButton()
        self.unique_chart_save_btn.setCheckable(True)
        self.unique_chart_save_btn.setText('OFF')
        self.unique_chart_save_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)
        self.unique_chart_save_btn.clicked.connect(self.on_chart_saving_btn_clicked)  # noqa
        self.layout.addWidget(self.unique_chart_save_btn)

        label = QLabel()
        label.setText('Show Results:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.show_sim_results_btn = QPushButton()
        self.show_sim_results_btn.setCheckable(True)
        self.show_sim_results_btn.setText('ON')
        self.show_sim_results_btn.setStyleSheet(self.toggle_btn_enabled_stylesheet)
        self.show_sim_results_btn.clicked.connect(self.on_show_results_btn_clicked)  # noqa
        self.layout.addWidget(self.show_sim_results_btn)

        self.run_btn = QPushButton()
        self.run_btn.setFixedSize(60, 30)
        self.run_btn.setText('RUN')
        self.run_btn.clicked.connect(self.on_run_btn_clicked)  # noqa
        self.run_btn.setStyleSheet(self.run_btn_stylesheet)
        self.layout.addWidget(self.run_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.error_message_box = QLabel()
        self.error_message_box.setStyleSheet(self.error_label_style_sheet)
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
            self.logging_btn.setStyleSheet(self.toggle_btn_enabled_stylesheet)
        else:
            self.simulation_logging = False
            self.logging_btn.setText('OFF')
            self.logging_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)

    def on_reporting_btn_clicked(self):
        if self.reporting_btn.isChecked():
            self.simulation_reporting = True
            self.reporting_btn.setText('ON')
            self.reporting_btn.setStyleSheet(self.toggle_btn_enabled_stylesheet)
        else:
            self.simulation_reporting = False
            self.reporting_btn.setText('OFF')
            self.reporting_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)

    def on_chart_saving_btn_clicked(self):
        if self.unique_chart_save_btn.isChecked():
            self.simulation_unique_chart_saving = True
            self.unique_chart_save_btn.setText('ON')
            self.unique_chart_save_btn.setStyleSheet(self.toggle_btn_enabled_stylesheet)
        else:
            self.simulation_unique_chart_saving = False
            self.unique_chart_save_btn.setText('OFF')
            self.unique_chart_save_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)

    def on_show_results_btn_clicked(self):
        if self.show_sim_results_btn.isChecked():
            self.simulation_show_results_window = True
            self.show_sim_results_btn.setText('ON')
            self.show_sim_results_btn.setStyleSheet(self.toggle_btn_enabled_stylesheet)
        else:
            self.simulation_show_results_window = False
            self.show_sim_results_btn.setText('OFF')
            self.show_sim_results_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)

    def on_simulation_length_cbox_index_changed(self, index):
        if index == 0:
            self.simulation_length = SECONDS_1_YEAR
        elif index == 1:
            self.simulation_length = SECONDS_2_YEAR
        elif index == 2:
            self.simulation_length = SECONDS_5_YEAR

    def on_run_btn_clicked(self):
        # load the strategy from the JSON file into a strategy python dict

        strategy_filepath = self.strategy_selection_box.strategy_filepath

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

        # inject the unix equivalent dates from the combobox to the dict
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
            self.simulation_unique_chart_saving)

        # all error checks have passed, can now clear the error message box
        self.error_message_box.setText('')

        # begin the simulation and progress checking timer
        self.simulation_result_window.begin()

        if self.simulation_show_results_window:
            # show the results window if option is checked
            self.simulation_result_window.showMaximized()


class MultiConfigTab(QWidget):
    text_box_stylesheet = """background-color: #303134;color:#FFF;border-width:0px;border-radius:10px;height:25px;
        text-indent:3px;"""

    select_file_btn_stylesheet = """background-color: #303134;color:#FFF;border-width:0px;border-radius:10px;
        height:25px;"""

    combobox_stylesheet = """background-color: #303134;color:#FFF;border-width:0px;border-radius:10px;height:25px;
        text-indent:3px;"""

    line_edit_stylesheet = """background-color:#303134;color:#FFF;border-width:0px;border-radius:10px;height:25px;
        text-indent:5px;"""

    toggle_btn_enabled_stylesheet = """background-color:#04ba5f;margin-left:auto;margin-right:auto;
        width:40%;height:25px;border-radius:10px;"""

    toggle_btn_disabled_stylesheet = """background-color: #303134;margin-left: auto;
            margin-right:auto;width: 40%;height:25px;border-radius: 10px;"""

    run_btn_stylesheet = """
            QPushButton
            {
                background-color: #04ba5f;
                color: #FFF;
                border-radius: 10px;
            }
            QPushButton:hover
            {
                background-color: #04ba50;
            }
            """

    error_label_style_sheet = """color:#dc143c;"""

    def __init__(self):
        super().__init__()
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

        # layout type
        self.layout = QVBoxLayout()

        label = QLabel()
        label.setText('Strategy:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.strategy_selection_box = StrategySelection()
        self.strategy_selection_box.setStyleSheet(self.select_file_btn_stylesheet)
        self.layout.addWidget(self.strategy_selection_box)
        self.strategy_studio_btn = QPushButton()
        self.strategy_studio_btn.setText('Strategy Studio (beta)')
        self.strategy_studio_btn.clicked.connect(self.on_strategy_studio_btn_clicked)  # noqa
        self.strategy_studio_btn.setStyleSheet(self.select_file_btn_stylesheet)
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

        self.simulation_length_cbox.setStyleSheet(self.combobox_stylesheet)
        self.simulation_length_cbox.currentIndexChanged.connect(self.on_simulation_length_cbox_index_changed)  # noqa
        self.layout.addWidget(self.simulation_length_cbox)

        label = QLabel()
        label.setText('Simulation Symbols:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.symbol_tbox = QLineEdit()
        self.symbol_tbox.setText("MSFT, AAPL")
        self.symbol_tbox.setStyleSheet(self.line_edit_stylesheet)
        self.layout.addWidget(self.symbol_tbox)

        label = QLabel()
        label.setText('Initial Balance:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.balance_tbox = QLineEdit()
        self.balance_tbox.setText('1000.0')
        self.onlyFloat = QDoubleValidator()
        self.balance_tbox.setValidator(self.onlyFloat)
        self.balance_tbox.setStyleSheet(self.line_edit_stylesheet)
        self.layout.addWidget(self.balance_tbox)

        label = QLabel()
        label.setText('Logging:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.logging_btn = QPushButton()
        self.logging_btn.setCheckable(True)
        self.logging_btn.setText('OFF')
        self.logging_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)
        self.logging_btn.clicked.connect(self.on_logging_btn_clicked)  # noqa
        self.layout.addWidget(self.logging_btn)

        label = QLabel()
        label.setText('Reporting:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.reporting_btn = QPushButton()
        self.reporting_btn.setCheckable(True)
        self.reporting_btn.setText('OFF')
        self.reporting_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)
        self.reporting_btn.clicked.connect(self.on_reporting_btn_clicked)  # noqa
        self.layout.addWidget(self.reporting_btn)

        label = QLabel()
        label.setText('Save Unique Charts:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.unique_chart_save_btn = QPushButton()
        self.unique_chart_save_btn.setCheckable(True)
        self.unique_chart_save_btn.setText('OFF')
        self.unique_chart_save_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)
        self.unique_chart_save_btn.clicked.connect(self.on_chart_saving_btn_clicked)  # noqa
        self.layout.addWidget(self.unique_chart_save_btn)

        label = QLabel()
        label.setText('Show Results:')
        label.setStyleSheet("""color: #FFF;""")
        self.layout.addWidget(label)

        self.show_sim_results_btn = QPushButton()
        self.show_sim_results_btn.setCheckable(True)
        self.show_sim_results_btn.setText('ON')
        self.show_sim_results_btn.setStyleSheet(self.toggle_btn_enabled_stylesheet)
        self.show_sim_results_btn.clicked.connect(self.on_show_results_btn_clicked)  # noqa
        self.layout.addWidget(self.show_sim_results_btn)

        self.run_btn = QPushButton()
        self.run_btn.setFixedSize(60, 30)
        self.run_btn.setText('RUN')
        self.run_btn.clicked.connect(self.on_run_btn_clicked)  # noqa
        self.run_btn.setStyleSheet(self.run_btn_stylesheet)
        self.layout.addWidget(self.run_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.error_message_box = QLabel()
        self.error_message_box.setStyleSheet(self.error_label_style_sheet)
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
            self.logging_btn.setStyleSheet(self.toggle_btn_enabled_stylesheet)
        else:
            self.simulation_logging = False
            self.logging_btn.setText('OFF')
            self.logging_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)

    def on_reporting_btn_clicked(self):
        if self.reporting_btn.isChecked():
            self.simulation_reporting = True
            self.reporting_btn.setText('ON')
            self.reporting_btn.setStyleSheet(self.toggle_btn_enabled_stylesheet)
        else:
            self.simulation_reporting = False
            self.reporting_btn.setText('OFF')
            self.reporting_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)

    def on_chart_saving_btn_clicked(self):
        if self.unique_chart_save_btn.isChecked():
            self.simulation_unique_chart_saving = True
            self.unique_chart_save_btn.setText('ON')
            self.unique_chart_save_btn.setStyleSheet(self.toggle_btn_enabled_stylesheet)
        else:
            self.simulation_unique_chart_saving = False
            self.unique_chart_save_btn.setText('OFF')
            self.unique_chart_save_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)

    def on_show_results_btn_clicked(self):
        if self.show_sim_results_btn.isChecked():
            self.simulation_show_results_window = True
            self.show_sim_results_btn.setText('ON')
            self.show_sim_results_btn.setStyleSheet(self.toggle_btn_enabled_stylesheet)
        else:
            self.simulation_show_results_window = False
            self.show_sim_results_btn.setText('OFF')
            self.show_sim_results_btn.setStyleSheet(self.toggle_btn_disabled_stylesheet)

    def on_simulation_length_cbox_index_changed(self, index):
        if index == 0:
            self.simulation_length = SECONDS_1_YEAR
        elif index == 1:
            self.simulation_length = SECONDS_2_YEAR
        elif index == 2:
            self.simulation_length = SECONDS_5_YEAR

    def on_run_btn_clicked(self):
        # load the strategy from the JSON file into a strategy python dict
        strategy_filepath = self.strategy_selection_box.strategy_filepath
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

        # inject the unix equivalent dates from the combobox to the dict
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
            self.simulation_unique_chart_saving)

        # all error checks have passed, can now clear the error message box
        self.error_message_box.setText('')

        # begin the simulation and progress checking timer
        self.simulation_result_window.begin()

        if self.simulation_show_results_window:
            # show the results window if option is checked
            self.simulation_result_window.showMaximized()


class StrategySelection(QWidget):
    filepath_stylesheet = """background-color: #303134;color: #FFF;"""

    btn_stylesheet = """background-color: #303134;color: #FFF;"""

    def __init__(self):
        super().__init__()

        self.strategy_filepath = None

        self.layout = QHBoxLayout()

        self.filepath_box = QLabel()
        self.filepath_box.setStyleSheet(self.filepath_stylesheet)
        self.layout.addWidget(self.filepath_box)

        self.select_file_btn = QPushButton()
        self.select_file_btn.setText('Select File')
        self.select_file_btn.clicked.connect(self.on_select_file_btn_click)  # noqa
        self.select_file_btn.setStyleSheet(self.btn_stylesheet)
        self.layout.addWidget(self.select_file_btn)

        self.setLayout(self.layout)

    def on_select_file_btn_click(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dlg.setNameFilter("JSON (*.json)")
        if dlg.exec():
            filenames = dlg.selectedFiles()
            self.strategy_filepath = filenames[0]
            self.filepath_box.setText(self.strategy_filepath)
