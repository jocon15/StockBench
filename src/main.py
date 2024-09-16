import os
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication
from StockBench.gui.application import ConfigMainWindow
from StockBench.caching.file_cache import load_cache_file


def main():
    # ensure that the cache file is loaded
    load_cache_file()
    # must create the QApplication before QPixmap to avoid errors
    app = QApplication(sys.argv)
    splash_pix = QtGui.QPixmap(os.path.join('resources', 'images', 'candle.png'))
    splash = QtWidgets.QSplashScreen(splash_pix)
    splash.show()
    splash.showMessage("Loading GUI application...", color=QColor(255, 255, 255),
                       alignment=Qt.AlignmentFlag.AlignBaseline)
    window = ConfigMainWindow(splash)
    window.show()

    app.exec()


if __name__ == '__main__':
    main()
