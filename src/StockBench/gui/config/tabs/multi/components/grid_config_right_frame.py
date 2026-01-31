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

    def __init__(self, on_logging_btn_clicked: Callable, on_reporting_btn_clicked: Callable,
                 on_chart_saving_btn_clicked: Callable, data_and_charts_btn_selected: Callable,
                 data_only_btn_selected: Callable) -> None:
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

        self.reporting_label = QLabel()
        self.reporting_label.setText('Reporting:')
        self.reporting_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(self.reporting_label)

        self.reporting_btn = QPushButton()
        self.reporting_btn.setCheckable(True)
        self.reporting_btn.setText(self.OFF)
        self.reporting_btn.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)
        self.reporting_btn.clicked.connect(lambda: on_reporting_btn_clicked(self.reporting_btn))  # noqa
        self.layout.addWidget(self.reporting_btn)

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

        self.results_depth_label = QLabel()
        self.results_depth_label.setText('Results Depth:')
        self.results_depth_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(self.results_depth_label)

        self.data_and_charts_radio_btn = QRadioButton("Data and Charts")
        self.data_and_charts_radio_btn.toggled.connect(data_and_charts_btn_selected)  # noqa
        self.data_and_charts_radio_btn.setStyleSheet(Palette.RADIO_BTN_STYLESHEET)
        self.data_and_charts_radio_btn.toggle()  # set data and charts as default
        self.layout.addWidget(self.data_and_charts_radio_btn)

        self.data_only_radio_btn = QRadioButton("Data Only")
        self.data_only_radio_btn.toggled.connect(data_only_btn_selected)  # noqa
        self.data_only_radio_btn.setStyleSheet(Palette.RADIO_BTN_STYLESHEET)
        self.layout.addWidget(self.data_only_radio_btn)

        self.layout.addStretch()

        self.setLayout(self.layout)
