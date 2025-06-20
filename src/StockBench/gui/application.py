from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel
from PyQt6 import QtGui

from StockBench.gui.palette.palette import Palette
from StockBench.gui.config.tabs.singular_config_tab import SingularConfigTab
from StockBench.gui.config.tabs.multi_config_tab import MultiConfigTab
from StockBench.gui.config.tabs.compare_config_tab import CompareConfigTab
from StockBench.gui.config.tabs.folder_config_tab import FolderConfigTab
from StockBench.gui.configuration import AppConfiguration


class ConfigMainWindow(QMainWindow):
    WIDTH = 400
    HEIGHT = 680

    def __init__(self, splash, config: AppConfiguration):
        super().__init__()
        self.splash = splash

        # main window styling (do it first to prevent window shifting)
        self.setWindowIcon(QtGui.QIcon(Palette.CANDLE_ICON))
        self.setWindowTitle('Configuration')
        # set window geometry
        self.__set_geometry()

        self.layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(SingularConfigTab(), "Single")
        self.tab_widget.addTab(MultiConfigTab(), "Multi")
        self.tab_widget.addTab(CompareConfigTab(), "Compare")
        self.tab_widget.addTab(FolderConfigTab(), "Folder")
        self.tab_widget.setStyleSheet(Palette.TAB_WIDGET_STYLESHEET)
        self.layout.addWidget(self.tab_widget)

        self.version_label = QLabel()
        self.version_label.setStyleSheet(Palette.HINT_LABEL_STYLESHEET)
        self.version_label.setText(f'StockBench {config.version_number}')
        self.layout.addWidget(self.version_label)

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
