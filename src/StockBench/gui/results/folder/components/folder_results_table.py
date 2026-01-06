from typing import Union

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QAbstractItemView, \
    QHeaderView, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QFont
from StockBench.gui.palette.palette import Palette
from StockBench.models.constants.simulation_results_constants import *


class FolderResultsTable(QFrame):
    TABLE_HEADERS = ['Strategy', 'Trades Made', 'Effectiveness (%)', 'Total PL ($)', 'Average PL ($)',
                     'Median PL ($)', 'Stddev PL ($)', 'Average PLPC (%)',
                     'Median PLPC (%)', 'Stddev PLPC (%)']

    WHITE_BRUSH = QColor(255, 255, 255)
    GREEN_BRUSH = QBrush(QColor(4, 186, 95))
    RED_BRUSH = QBrush(QColor(209, 82, 84))

    TABLE_HEADER_FONT_SIZE = 16

    TABLE_VALUE_ROW_HEIGHT = 50
    TABLE_VALUE_FONT_SIZE = 13

    FRAME_STYLESHEET = """
        #folderResultsTable {
            border: 1px solid grey; 
            border-radius: 25px; 
            padding: 5px;
        }
        """

    def __init__(self, strategies):
        super().__init__()
        self.layout = QVBoxLayout()

        self.setMinimumWidth(800)
        self.setObjectName("folderResultsTable")  # apply styles based on id (must inherit from QFrame)
        self.setStyleSheet(self.FRAME_STYLESHEET)

        self.toggle_heatmap_btn = QPushButton()
        self.toggle_heatmap_btn.setFixedSize(400, 30)
        self.toggle_heatmap_btn.setText('Toggle Table Column Heatmap')
        self.toggle_heatmap_btn.setCheckable(True)
        self.toggle_heatmap_btn.clicked.connect(self.on_toggle_table_heatmap)  # noqa
        self.toggle_heatmap_btn.setStyleSheet(Palette.SECONDARY_BTN)  # default off
        self.layout.addWidget(self.toggle_heatmap_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        self.table = QTableWidget()
        self.table.setRowCount(len(strategies))
        self.table.setColumnCount(len(self.TABLE_HEADERS))
        self.__setup_table_headers()
        self.table.verticalHeader().hide()
        self.table.setFrameStyle(0)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # add table to widget with stretch factor of 1, prevents table from shrinking when other widgets (error message)
        # added to layout, other widgets have default factor of 0, causing the layout to favor stretching of the table
        self.layout.addWidget(self.table, 1)

        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        results = simulation_results['results']

        font = QFont()
        font.setPointSize(self.TABLE_VALUE_FONT_SIZE)

        for row, result in enumerate(results):
            cell_widgets = [
                QTableWidgetItem(f'{result[STRATEGY_KEY]}'),
                QTableWidgetItem(f'{result[TRADES_MADE_KEY]}'),
                QTableWidgetItem(f'{result[EFFECTIVENESS_KEY]:,.2f}'),
                QTableWidgetItem(f'{result[TOTAL_PL_KEY]:,.2f}'),
                QTableWidgetItem(f'{result[AVERAGE_PL_KEY]:,.2f}'),
                QTableWidgetItem(f'{result[MEDIAN_PL_KEY]:,.2f}'),
                QTableWidgetItem(f'{result[STANDARD_DEVIATION_PL_KEY]:,.2f}'),
                QTableWidgetItem(f'{result[AVERAGE_PLPC_KEY]:,.3f}'),
                QTableWidgetItem(f'{result[MEDIAN_PLPC_KEY]:,.3f}'),
                QTableWidgetItem(f'{result[STANDARD_DEVIATION_PLPC_KEY]:,.3f}')
            ]

            self.table.setRowHeight(row, self.TABLE_VALUE_ROW_HEIGHT)
            for col, cell_widget in enumerate(cell_widgets):
                cell_widget.setForeground(QBrush(self.WHITE_BRUSH))
                cell_widget.setFont(font)
                self.table.setItem(row, col, cell_widget)

        self.__apply_green_red_values()

    def on_toggle_table_heatmap(self):
        # check if data exists in the table
        if self.table.item(1, 1) is not None:
            if self.toggle_heatmap_btn.isChecked():
                self._apply_table_heatmap()
            else:
                self._remove_table_heatmap()

    def _apply_table_heatmap(self):
        hsv_range = 100

        for column_index in range(1, len(self.TABLE_HEADERS)):
            column_values = []
            for row_index in range(self.table.rowCount()):
                cell_value_str = self.table.item(row_index, column_index).text()
                cell_value_float = self.__convert_comma_str_to_float(cell_value_str)
                column_values.append(cell_value_float)
            min_value = min(column_values)
            value_range = max(column_values) - min_value
            conversion_value = value_range / hsv_range

            for row_index in range(self.table.rowCount()):
                cell_value_str = self.table.item(row_index, column_index).text()
                cell_value_float = self.__convert_comma_str_to_float(cell_value_str)
                dif = cell_value_float - min_value
                hue_value = int(dif / conversion_value)
                color = QColor.fromHsv(hue_value, 255, 191, 191)
                self.table.item(row_index, column_index).setForeground(QBrush(self.WHITE_BRUSH))
                self.table.item(row_index, column_index).setBackground(QBrush(color))

    def _remove_table_heatmap(self):
        for column_index in range(1, len(self.TABLE_HEADERS)):
            for row_index in range(self.table.rowCount()):
                self.table.item(row_index, column_index).setBackground(QBrush(QColor(32, 33, 36)))

        self.__apply_green_red_values()

    def __setup_table_headers(self):
        background_color = QColor(33, 39, 51)
        header_font = QFont()
        header_font.setPointSize(self.TABLE_HEADER_FONT_SIZE)

        for i, header in enumerate(self.TABLE_HEADERS):
            item = QTableWidgetItem(header)
            item.setFont(header_font)
            item.setBackground(background_color)
            self.table.setHorizontalHeaderItem(i, item)

    def __apply_green_red_values(self):
        if self.table.item(1, 1) is not None:
            # starts at total PL (index: 3)
            for column_index in range(3, len(self.TABLE_HEADERS)):
                if column_index == 6 or column_index == 9:
                    # skip stddev values
                    continue

                for row_index in range(self.table.rowCount()):
                    value = self.table.item(row_index, column_index).text()
                    self.table.item(row_index, column_index).setForeground(
                        self.__select_red_green_brush(value)
                    )

    def __select_red_green_brush(self, value: Union[str, int, float]) -> QBrush:
        if type(value) is str:
            value = self.__convert_comma_str_to_float(value)
        if float(value) >= 0:
            return self.GREEN_BRUSH
        return self.RED_BRUSH

    @staticmethod
    def __convert_comma_str_to_float(value: str) -> float:
        clean_str = value.replace(",", "")
        return float(clean_str)
