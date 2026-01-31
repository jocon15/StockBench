from typing import Callable

from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QRadioButton

from StockBench.gui.palette.palette import Palette


class GridConfigRightFrame(QFrame):
    FRAME_WIDTH = 300

    ON = 'ON'
    OFF = 'OFF'

    FRAME_STYLESHEET = """
            #gridConfigRightFrame {
                border-left: 1px solid grey;
                padding-left: 25px;
            }
            """

    def __init__(self, on_logging_btn_clicked: Callable, on_chart_saving_btn_clicked: Callable) -> None:
        super().__init__()
        self.setFixedWidth(self.FRAME_WIDTH)
        self.setObjectName("gridConfigRightFrame")  # apply styles based on id (must inherit from QFrame)
        self.setStyleSheet(self.FRAME_STYLESHEET)

        self.layout = QVBoxLayout()

        self.logging_label = QLabel()
        self.logging_label.setText('Logging:')
        self.logging_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(self.logging_label)

        self.logging_btn = QPushButton()
        self.logging_btn.setCheckable(True)
        self.logging_btn.setText(self.OFF)
        self.logging_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)
        self.logging_btn.clicked.connect(lambda: on_logging_btn_clicked(self.logging_btn))  # noqa
        self.layout.addWidget(self.logging_btn)

        self.unique_chart_save_label = QLabel()
        self.unique_chart_save_label.setText('Save Unique Charts:')
        self.unique_chart_save_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(self.unique_chart_save_label)

        self.unique_chart_save_btn = QPushButton()
        self.unique_chart_save_btn.setCheckable(True)
        self.unique_chart_save_btn.setText(self.OFF)
        self.unique_chart_save_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)
        self.unique_chart_save_btn.clicked.connect(lambda: on_chart_saving_btn_clicked(self.unique_chart_save_btn))  # noqa
        self.layout.addWidget(self.unique_chart_save_btn)

        self.layout.addStretch()

        self.setLayout(self.layout)
