from PyQt6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtCore import Qt, QTimer
from StockBench.gui.windows.base.overview_tab import OverviewTab
from StockBench.gui.windows.multi.tabs.multi_overview_tab import MultiMetadataOverviewTable


class FolderResultsTab(OverviewTab):
    def __init__(self, strategies, progress_observers):
        super().__init__()
        self.overview_side_bar = FolderOverviewSidebar(progress_observers)
        self.layout.addWidget(self.overview_side_bar)
        self.overview_side_bar.setMaximumWidth(300)

        self.results_table = FolderResultsTable(strategies)
        self.layout.addWidget(self.results_table)

        # apply the layout
        self.setLayout(self.layout)

    def render_data(self, simulation_results):
        self.overview_side_bar.render_data(simulation_results)
        self.results_table.render_data(simulation_results)

    def update_error_message(self, message):
        # pass the error down
        self.overview_side_bar.update_error_message(message)


class FolderResultsTable(QWidget):
    TABLE_HEADERS = ['strategy', 'Trades Made', 'Effectiveness', 'Total P/L', 'Average P/L', 'Median P/L', 'Stddev']

    CELL_TEXT_COLOR = QColor(255, 255, 255)

    def __init__(self, strategies):
        super().__init__()
        self.layout = QVBoxLayout()

        # table
        self.table = QTableWidget()
        self.table.setRowCount(len(strategies))
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(self.TABLE_HEADERS)
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


class FolderOverviewSidebar(QWidget):
    OUTPUT_BOX_STYLESHEET = """color: #fff; background-color: #303136; border-radius: 8px;border: 0px; padding: 5px; 
        max-height: 300px;"""

    EXPORT_BTN_STYLESHEET = """background-color: #303134;color:#FFF;border-width:0px;border-radius:10px;height:25px;"""

    HEADER_STYLESHEET = """max-height:45px; color:#FFF;font-size:20px;font-weight:bold;"""

    def __init__(self, progress_observers):
        super().__init__()
        self.progress_observers = progress_observers

        # define layout type
        self.layout = QVBoxLayout()

        # metadata header
        self.metadata_header = QLabel()
        self.metadata_header.setText('Metadata')
        self.metadata_header.setStyleSheet(self.HEADER_STYLESHEET)

        # results header
        self.results_header = QLabel()
        self.results_header.setText('Simulation Results')
        self.results_header.setStyleSheet(self.HEADER_STYLESHEET)

        # export JSON button
        self.export_json_btn = QPushButton()
        self.export_json_btn.setText('Export to Clipboard (JSON)')
        self.export_json_btn.setStyleSheet(self.EXPORT_BTN_STYLESHEET)
        # self.export_json_btn.clicked.connect(self.on_export_json_btn_clicked)  # noqa

        # export excel button
        self.export_excel_btn = QPushButton()
        self.export_excel_btn.setText('Export to ClipBoard (excel)')
        self.export_excel_btn.setStyleSheet(self.EXPORT_BTN_STYLESHEET)
        # self.export_excel_btn.clicked.connect(self.on_export_excel_btn_clicked)  # noqa

        # output box (terminal)
        self.output_box = QListWidget()
        self.output_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.output_box.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.output_box.setStyleSheet(self.OUTPUT_BOX_STYLESHEET)

        # status header
        self.status_header = QLabel()
        self.status_header.setText('Status')
        self.status_header.setStyleSheet(self.HEADER_STYLESHEET)

        # add components to the layout
        self.layout.addWidget(self.metadata_header)

        self.metadata_table = MultiMetadataOverviewTable()
        self.layout.addWidget(self.metadata_table)

        self.layout.addWidget(self.results_header)

        self.layout.addWidget(self.export_json_btn)

        self.layout.addWidget(self.export_excel_btn)

        # pushes the status header and output box to the bottom
        self.layout.addStretch()

        self.layout.addWidget(self.status_header)
        self.layout.addWidget(self.output_box)

        # apply the layout
        self.setLayout(self.layout)

        # timer to periodically read from the progress observer and update output box
        self.timer = QTimer()
        # start the timer to update the output box every 100ms
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.__update_output_box)  # noqa
        self.timer.start()

    def update_error_message(self, message):
        # handle the passed down error message by adding it to the output box
        list_item = QListWidgetItem(message)
        list_item.setForeground(QColor('red'))
        self.output_box.addItem(list_item)

    def __update_output_box(self):
        """Update the output box with messages from the progress observer."""
        all_observers_complete = True
        for progress_observer in self.progress_observers:
            if not progress_observer.is_analytics_completed():
                all_observers_complete = False
            messages = progress_observer.get_messages()
            for message in messages:
                list_item = QListWidgetItem(str(message.msg))
                if message.levelname == 'WARNING':
                    list_item.setForeground(QColor('yellow'))
                else:
                    list_item.setForeground(QColor('grey'))
                self.output_box.addItem(list_item)
            # scroll the output box to the bottom
            self.output_box.scrollToBottom()

        if all_observers_complete:
            # stop the timer
            self.timer.stop()

    def render_data(self, simulation_results):
        # extract the results list
        results = simulation_results['results']
        # select the first result to use as a template
        result_to_use = results[0]
        # extract the elapsed time and inject it into the result to use (represents the entire sim time)
        result_to_use['elapsed_time'] = simulation_results['elapsed_time']
        self.metadata_table.render_data(result_to_use)
