# coding: utf-8
# SOURCE: https://gist.github.com/sergeyfarin/c689fd0171f95865055fad857579bc94

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QVBoxLayout, QWidget, QTabWidget, \
    QLineEdit, QLabel
from PyQt6 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.w = None  # No external window yet.
        self.button = QPushButton("Push for Window")
        self.button.clicked.connect(self.show_new_window) # noqa - disables false warning for connect function
        self.setCentralWidget(self.button)

    def __del__(self):
        self.graph_window = None

    def show_new_window(self, checked):
        if self.w is None:
            self.w = GraphWindow()
            self.w.show()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.


# Subclass QMainWindow to customize your application's main window
class GraphWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.w = None
        main_layout = QGridLayout()

        self.webEview = QtWebEngineWidgets.QWebEngineView()
        self.webEview.load(QtCore.QUrl().fromLocalFile(
            os.path.split(os.path.abspath(__file__))[0] + r'\ema_ex.html'))

        self.button = QPushButton("Press Me!")
        self.button.clicked.connect(self.show_new_window)  # noqa - disables false warning for connect function

        main_layout.addWidget(self.webEview)
        main_layout.addWidget(self.button)
        self.setLayout(main_layout)

        self.setWindowTitle("Plotly test")

    def __del__(self):
        self.W = None

    def show_new_window(self):
        self.w = AuxWindow()
        self.w.show()


class AuxWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Another Window")
        layout.addWidget(self.label)
        self.setLayout(layout)


app = QApplication(sys.argv)
demo = MainWindow()
demo.show()

sys.exit(app.exec())
