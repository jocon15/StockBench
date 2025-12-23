from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor
from StockBench.gui.palette.palette import Palette
from StockBench.models.constants.simulation_results_constants import *


class FolderResultsTable(QWidget):
    TABLE_HEADERS = ['Strategy', 'Trades Made', 'Effectiveness (%)', 'Total PL ($)', 'Average PL ($)',
                     'Median PL ($)', 'Stddev (P) PL ($)', 'Average PLPC (%)',
                     'Median PLPC (%)', 'Stddev (P) PLPC (%)']

    CELL_TEXT_COLOR = QColor(255, 255, 255)

    TABLE_COLUMN_COUNT = 10

    def __init__(self, strategies):
        super().__init__()
        self.layout = QVBoxLayout()

        self.toggle_heatmap_btn = QPushButton()
        self.toggle_heatmap_btn.setFixedSize(400, 30)
        self.toggle_heatmap_btn.setText('Toggle Table Column Heatmap')
        self.toggle_heatmap_btn.setCheckable(True)
        self.toggle_heatmap_btn.clicked.connect(self.on_toggle_table_heatmap)  # noqa
        self.toggle_heatmap_btn.setStyleSheet(Palette.SECONDARY_BTN)  # default off
        self.layout.addWidget(self.toggle_heatmap_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        self.table = QTableWidget()
        self.table.setRowCount(len(strategies))
        self.table.setColumnCount(self.TABLE_COLUMN_COUNT)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setHorizontalHeaderLabels(self.TABLE_HEADERS)
        self.table.verticalHeader().setVisible(False)
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        results = simulation_results['results']

        for row, result in enumerate(results):
            strategy_cell = QTableWidgetItem(f'{result[STRATEGY_KEY]}')
            trades_made_cell = QTableWidgetItem(f'{result[TRADES_MADE_KEY]}')
            effectiveness_cell = QTableWidgetItem(f'{result[EFFECTIVENESS_KEY]:,.2f}')
            total_pl_cell = QTableWidgetItem(f'{result[TOTAL_PL_KEY]:,.2f}')
            avg_pl_cell = QTableWidgetItem(f'{result[AVERAGE_PL_KEY]:,.2f}')
            median_pl_cell = QTableWidgetItem(f'{result[MEDIAN_PL_KEY]:,.2f}')
            stddev_pl_cell = QTableWidgetItem(f'{result[STANDARD_DEVIATION_PL_KEY]:,.2f}')
            avg_plpc_cell = QTableWidgetItem(f'{result[AVERAGE_PLPC_KEY]:,.2f}')
            median_plpc_cell = QTableWidgetItem(f'{result[MEDIAN_PLPC_KEY]:,.2f}')
            stddev_plpc_cell = QTableWidgetItem(f'{result[STANDARD_DEVIATION_PLPC_KEY]:,.2f}')

            strategy_cell.setForeground(QBrush(self.CELL_TEXT_COLOR))
            trades_made_cell.setForeground(QBrush(self.CELL_TEXT_COLOR))
            effectiveness_cell.setForeground(QBrush(self.CELL_TEXT_COLOR))
            total_pl_cell.setForeground(QBrush(self.CELL_TEXT_COLOR))
            avg_pl_cell.setForeground(QBrush(self.CELL_TEXT_COLOR))
            median_pl_cell.setForeground(QBrush(self.CELL_TEXT_COLOR))
            stddev_pl_cell.setForeground(QBrush(self.CELL_TEXT_COLOR))
            avg_plpc_cell.setForeground(QBrush(self.CELL_TEXT_COLOR))
            median_plpc_cell.setForeground(QBrush(self.CELL_TEXT_COLOR))
            stddev_plpc_cell.setForeground(QBrush(self.CELL_TEXT_COLOR))

            self.table.setItem(row, 0, strategy_cell)
            self.table.setItem(row, 1, trades_made_cell)
            self.table.setItem(row, 2, effectiveness_cell)
            self.table.setItem(row, 3, total_pl_cell)
            self.table.setItem(row, 4, avg_pl_cell)
            self.table.setItem(row, 5, median_pl_cell)
            self.table.setItem(row, 6, stddev_pl_cell)
            self.table.setItem(row, 7, avg_plpc_cell)
            self.table.setItem(row, 8, median_plpc_cell)
            self.table.setItem(row, 9, stddev_plpc_cell)

    def on_toggle_table_heatmap(self):
        # check if data exists in the table
        if self.table.item(1, 1) is not None:
            if self.toggle_heatmap_btn.isChecked():
                self._apply_table_heatmap()
            else:
                self._remove_table_heatmap()

    def _apply_table_heatmap(self):
        hsv_range = 100

        for column_index in range(1, self.TABLE_COLUMN_COUNT):
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
                self.table.item(row_index, column_index).setBackground(QBrush(color))

    def _remove_table_heatmap(self):
        for column_index in range(1, self.TABLE_COLUMN_COUNT):
            for row_index in range(self.table.rowCount()):
                self.table.item(row_index, column_index).setBackground(QBrush(QColor(32, 33, 36)))

    @staticmethod
    def __convert_comma_str_to_float(value: str) -> float:
        clean_str = value.replace(",", "")
        return float(clean_str)
