from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QComboBox, QLineEdit

from StockBench.gui.palette.palette import Palette


class GridConfigLeftFrame(QFrame):
    INPUT_WIDTH = 240

    def __init__(self, on_simulation_length_cbox_index_changed: Callable):
        super().__init__()

        self.setFixedWidth(300)

        self.layout = QVBoxLayout()

        self.simulation_length_label = QLabel()
        self.simulation_length_label.setText('Simulation Length:')
        self.simulation_length_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(self.simulation_length_label)

        self.simulation_length_cbox = QComboBox()
        self.simulation_length_cbox.addItem('1 Year')
        self.simulation_length_cbox.addItem('2 Year')
        self.simulation_length_cbox.addItem('5 Year')
        # set simulation length default to 1 year (must set attribute as well in application)
        self.simulation_length_cbox.setCurrentIndex(0)
        self.simulation_length_cbox.setStyleSheet(Palette.COMBOBOX_STYLESHEET)
        self.simulation_length_cbox.currentIndexChanged.connect(on_simulation_length_cbox_index_changed)  # noqa
        self.simulation_length_cbox.setFixedWidth(self.INPUT_WIDTH)
        self.layout.addWidget(self.simulation_length_cbox, alignment=Qt.AlignmentFlag.AlignCenter)

        label = QLabel()
        label.setText('Simulation Symbol:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.symbol_tbox = QLineEdit()
        self.symbol_tbox.setText("MSFT")
        self.symbol_tbox.setStyleSheet(Palette.LINE_EDIT_STYLESHEET)
        self.symbol_tbox.setFixedWidth(self.INPUT_WIDTH)
        self.layout.addWidget(self.symbol_tbox, alignment=Qt.AlignmentFlag.AlignCenter)

        self.initial_balance_label = QLabel()
        self.initial_balance_label.setText('Initial Balance:')
        self.initial_balance_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(self.initial_balance_label)

        self.initial_balance_tbox = QLineEdit()
        self.initial_balance_tbox.setText('1000.0')
        self.onlyFloat = QDoubleValidator()
        self.initial_balance_tbox.setValidator(self.onlyFloat)
        self.initial_balance_tbox.setStyleSheet(Palette.LINE_EDIT_STYLESHEET)
        self.initial_balance_tbox.setFixedWidth(self.INPUT_WIDTH)
        self.layout.addWidget(self.initial_balance_tbox, alignment=Qt.AlignmentFlag.AlignCenter)

        self.layout.addStretch()

        self.setLayout(self.layout)
