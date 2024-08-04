from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QListWidgetItem, QMessageBox
from PyQt6.QtGui import QBrush, QColor
from StockBench.gui.results.base.overview_tab import OverviewTab
from StockBench.gui.results.multi.tabs.multi_overview_tab import MultiMetadataOverviewTable
from StockBench.gui.results.base.overview_tab import OverviewSideBar
from StockBench.observers.progress_observer import ProgressObserver
from StockBench.gui.results.folder.components.folder_selection import FolderSelection
from StockBench.export.folder_results_exporter import FolderResultsExporter


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


class FolderOverviewSidebar(OverviewSideBar):
    def __init__(self, progress_observers):
        # pass a summy progress observer to the superclass as we are overriding the
        # update output box function now that we have a list of progress observers
        dummy_progress_observer = ProgressObserver()
        super().__init__(dummy_progress_observer)
        self.simulation_results_to_export = {}

        self.progress_observers = progress_observers

        # add components to the layout
        self.layout.addWidget(self.metadata_header)

        self.metadata_table = MultiMetadataOverviewTable()
        self.layout.addWidget(self.metadata_table)

        self.layout.addWidget(self.results_header)

        self.layout.addWidget(self.export_json_btn)

        self.folder_selection = FolderSelection()
        self.layout.addWidget(self.folder_selection)

        self.layout.addWidget(self.export_excel_btn)

        # pushes the status header and output box to the bottom
        self.layout.addStretch()

        self.layout.addWidget(self.status_header)

        self.layout.addWidget(self.output_box)

        # apply the layout
        self.setLayout(self.layout)

    def on_export_json_btn_clicked(self):
        if self.simulation_results_to_export:
            export_string = ''
            for result in self.simulation_results_to_export['results']:
                # copy and clean the results info
                result_dict = self._remove_extraneous_info(result)
                result_values = ''
                for key in result_dict.keys():
                    result_values += f'{result_dict[key]},'
                export_string += result_values + ' '

            # remove last comma from string
            export_string = export_string.rsplit(',', 1)[0]
            self._copy_to_clipboard(export_string)
        # if no results are available yet, nothing gets copied to the clipboard

    def on_export_excel_btn_clicked(self):
        # get the filepath from the ui component
        folder_path = self.folder_selection.folderpath_box.text()

        # export the data to the xlsx file
        exporter = FolderResultsExporter()
        filepath = exporter.export(self.simulation_results_to_export['results'], folder_path, 'FolderResults')

        # show a message box indicating the file was saved
        msgbox = QMessageBox()
        msgbox.setText(f'File has been saved to {filepath}')
        msgbox.setWindowTitle("Information MessageBox")
        msgbox.exec()

    def _update_output_box(self):
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

    def _remove_extraneous_info(self, results: dict) -> dict:
        """Remove info from the simulation results that is not relevant to exporting."""
        export_dict = results.copy()

        # remove extraneous data from exported results
        export_dict.pop('elapsed_time')
        export_dict.pop('buy_rule_analysis_chart_filepath')
        export_dict.pop('sell_rule_analysis_chart_filepath')
        export_dict.pop('position_analysis_chart_filepath')
        export_dict.pop('overview_chart_filepath')

        return export_dict

    def render_data(self, simulation_results):
        # save the results to allow exporting
        self.simulation_results_to_export = simulation_results
        # extract the results list
        results = simulation_results['results']
        # select the first result to use as a template
        result_to_use = results[0]
        # extract the elapsed time and inject it into the result to use (represents the entire sim time)
        result_to_use['elapsed_time'] = simulation_results['elapsed_time']
        self.metadata_table.render_data(result_to_use)
