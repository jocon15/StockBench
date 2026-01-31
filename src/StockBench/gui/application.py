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

        self.__stockbench_controller = StockBenchControllerFactory.get_controller_instance()

        # main window styling (done first to prevent window shifting)
        self.setWindowIcon(QtGui.QIcon(Palette.CANDLE_ICON_FILEPATH))
        self.setWindowTitle('Configuration')
        # SEE BOTTOM FOR CONFIG WINDOW SIZING!!!

        self.layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(SingularConfigTab(self.__update_geometry, self.__stockbench_controller), "Single")
        self.tab_widget.addTab(MultiConfigTab(self.__update_geometry, self.__stockbench_controller), "Multi")
        self.tab_widget.addTab(CompareConfigTab(self.__update_geometry, self.__stockbench_controller), "Compare")
        self.tab_widget.addTab(FolderConfigTab(self.__update_geometry, self.__stockbench_controller), "Folder")
        self.tab_widget.setStyleSheet(Palette.TAB_WIDGET_STYLESHEET)
        self.layout.addWidget(self.tab_widget)

        self.version_label = QLabel()
        self.version_label.setStyleSheet(Palette.HINT_LABEL_STYLESHEET)
        self.version_label.setText(f'StockBench {config.version_number}')
        self.layout.addWidget(self.version_label)

        widget = QWidget()
        widget.setStyleSheet(Palette.WINDOW_STYLESHEET)
        widget.setLayout(self.layout)

        self.setCentralWidget(widget)

        self.splash.close()

        # CONFIG WINDOW SIZING
        # we want the window to shrink to the size of the widgets but also be non-resizable
        # after the tabs are added, the following block shrinks the window to fit of the biggest tab and disables
        # resizing
        self.__update_geometry()

    def __update_geometry(self):
        """Updates the geometry of the main config window while maintaining the in-ability for manual resize.

        Use 1: Used to set the initial size of the main config window after tabs are added to the layout.
        Use 2: Callback for when the error message label is added to the layout, preventing other widget squishing by
            resizing the layout to fit all contained widgets.
        """
        self.updateGeometry()
        self.adjustSize()
        size = self.sizeHint()
        self.setMinimumSize(size)
        self.setMaximumSize(size)
