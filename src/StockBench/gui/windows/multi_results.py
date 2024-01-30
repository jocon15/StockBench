import os
import sys

from PyQt6 import QtCore, QtWebEngineWidgets
from PyQt6.QtWidgets import QVBoxLayout, QGridLayout, QHBoxLayout, QWidget, QLabel, QProgressBar, QFrame
from PyQt6.QtCore import QTimer, QThreadPool

# current directory (peripherals)
current = os.path.dirname(os.path.realpath(__file__))

# parent filepath (src)
parent = os.path.dirname(current)

# add the parent (src) to path
sys.path.append(parent)


class MultiResultsWindow(QWidget):
    pass
