from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout
from PyQt6.QtGui import QBrush, QColor


class FolderResultsTable(QWidget):
    TABLE_HEADERS = ['Strategy', 'Trades Made', 'Effectiveness', 'Total P/L', 'Average P/L', 'Median P/L',
                     'Stddev(P) P/L']

    CELL_TEXT_COLOR = QColor(255, 255, 255)

    def __init__(self, strategies):
        super().__init__()
        self.layout = QVBoxLayout()

        # table
        self.table = QTableWidget()
        self.table.setRowCount(len(strategies))
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(self.TABLE_HEADERS)
        self.table.verticalHeader().setVisible(False)
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

    def render_data(self, simulation_results: dict):
        results = simulation_results['results']

        for row, result in enumerate(results):
            strategy_cell = QTableWidgetItem(str(result['strategy']))
            trades_made_cell = QTableWidgetItem(str(result['trades_made']))
            effectiveness_cell = QTableWidgetItem(str(result['effectiveness']))
            total_pl_cell = QTableWidgetItem(str(result['total_profit_loss']))
            avg_pl_cell = QTableWidgetItem(str(result['average_profit_loss']))
            median_pl_cell = QTableWidgetItem(str(result['median_profit_loss']))
            stddev_pl_cell = QTableWidgetItem(str(result['standard_profit_loss_deviation']))

            strategy_cell.setForeground(QBrush(self.CELL_TEXT_COLOR))
            trades_made_cell.setForeground(QBrush(self.CELL_TEXT_COLOR))
            effectiveness_cell.setForeground(QBrush(self.CELL_TEXT_COLOR))
            total_pl_cell.setForeground(QBrush(self.CELL_TEXT_COLOR))
            avg_pl_cell.setForeground(QBrush(self.CELL_TEXT_COLOR))
            median_pl_cell.setForeground(QBrush(self.CELL_TEXT_COLOR))
            stddev_pl_cell.setForeground(QBrush(self.CELL_TEXT_COLOR))

            self.table.setItem(row, 0, strategy_cell)
            self.table.setItem(row, 1, trades_made_cell)
            self.table.setItem(row, 2, effectiveness_cell)
            self.table.setItem(row, 3, total_pl_cell)
            self.table.setItem(row, 4, avg_pl_cell)
            self.table.setItem(row, 5, median_pl_cell)
            self.table.setItem(row, 6, stddev_pl_cell)
