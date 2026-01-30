from typing import Callable

from PyQt6.QtWidgets import QFrame, QGridLayout

from StockBench.gui.config.tabs.compare.components.grid_config_left_frame import GridConfigLeftFrame
from StockBench.gui.config.tabs.compare.components.grid_config_right_frame import GridConfigRightFrame


class GridConfigFrame(QFrame):
    def __init__(self, on_simulation_length_cbox_index_changed: Callable, on_logging_btn_clicked: Callable,
                 on_reporting_btn_clicked: Callable, on_chart_saving_btn_clicked: Callable,
                 data_and_charts_btn_selected: Callable, data_only_btn_selected: Callable):
        super().__init__()

        self.layout = QGridLayout()

        self.left_frame = GridConfigLeftFrame(on_simulation_length_cbox_index_changed)
        self.right_frame = GridConfigRightFrame(on_logging_btn_clicked, on_reporting_btn_clicked,
                                                on_chart_saving_btn_clicked, data_and_charts_btn_selected,
                                                data_only_btn_selected)

        self.layout.addWidget(self.left_frame, 0, 0)
        self.layout.addWidget(self.right_frame, 0, 1)

        self.setLayout(self.layout)
