import os
import sys
import multiprocessing

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication

from StockBench.gui.application import ConfigMainWindow
from StockBench.caching.file_cache import load_cache_file
from StockBench.controllers.factories.configuration import ApplicationConfigurationFactory


def main():
    # ensure that the cache file is loaded
    load_cache_file()
    # must create the QApplication before QPixmap to avoid errors
    app = QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))  # won't work on windows style
    splash_pix = QtGui.QPixmap(os.path.join('resources', 'images', 'candle.png'))
    splash = QtWidgets.QSplashScreen(splash_pix)
    splash.show()
    splash.showMessage("Loading GUI application...", color=QColor(255, 255, 255),
                       alignment=Qt.AlignmentFlag.AlignBaseline)
    app_config = ApplicationConfigurationFactory.create_app_config()
    window = ConfigMainWindow(splash, app_config)
    window.show()

    app.exec()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
