from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel
from PyQt6 import QtGui

from StockBench.gui.config.tabs.compare.compare_config_tab import CompareConfigTab
from StockBench.gui.config.tabs.folder.folder_config_tab import FolderConfigTab
from StockBench.gui.config.tabs.singular.singular_config_tab import SingularConfigTab
from StockBench.gui.palette.palette import Palette
from StockBench.gui.config.tabs.multi.multi_config_tab import MultiConfigTab
from StockBench.gui.configuration import AppConfiguration
from StockBench.controllers.controller_factory import StockBenchControllerFactory


class ConfigMainWindow(QMainWindow):
    WIDTH = 650
    HEIGHT = 600

    def __init__(self, splash, config: AppConfiguration):
        super().__init__()
        self.splash = splash

        # get an instance of the controller for the application to use (reference passed to all results windows)
        self.__stockbench_controller = StockBenchControllerFactory.get_controller_instance()

        # main window styling (do it first to prevent window shifting)
        self.setWindowIcon(QtGui.QIcon(Palette.CANDLE_ICON))
        self.setWindowTitle('Configuration')
        # SEE BOTTOM FOR CONFIG WINDOW SIZING!!!

        self.layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(SingularConfigTab(self.__stockbench_controller), "Single")
        self.tab_widget.addTab(MultiConfigTab(self.__stockbench_controller), "Multi")
        self.tab_widget.addTab(CompareConfigTab(self.__stockbench_controller), "Compare")
        self.tab_widget.addTab(FolderConfigTab(self.__stockbench_controller), "Folder")
        self.tab_widget.setStyleSheet(Palette.TAB_WIDGET_STYLESHEET)
        self.layout.addWidget(self.tab_widget)

        self.version_label = QLabel()
        self.version_label.setStyleSheet(Palette.HINT_LABEL_STYLESHEET)
        self.version_label.setText(f'StockBench {config.version_number}')
        self.layout.addWidget(self.version_label)

        widget = QWidget()
        widget.setStyleSheet(Palette.WINDOW_STYLESHEET)
        widget.setLayout(self.layout)

        # set the central widget of the Window. Widget will expand to take up all the space in the window by default
        self.setCentralWidget(widget)

        self.splash.close()

        # CONFIG WINDOW SIZING
        # we want the window to shrink to the size of the widgets but also be non-resizable
        # after the tabs are added, the following block shrinks the window to fit of the biggest tab and disables
        # resizing
        self.updateGeometry()
        size = self.sizeHint()
        self.setMinimumSize(size)
        self.setMaximumSize(size)
