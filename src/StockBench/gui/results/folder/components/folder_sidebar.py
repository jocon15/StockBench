from PyQt6.QtWidgets import QListWidgetItem
from PyQt6.QtGui import QColor

from StockBench.controllers.export import MarkdownExporter
from StockBench.gui.results.multi.components.multi_sidebar_metadata_table import MultiMetadataSidebarTable
from StockBench.gui.results.base.overview_sidebar import OverviewSideBar
from StockBench.models.observers.progress_observer import ProgressObserver
from StockBench.gui.results.folder.components.folder_selector import FolderSelector
from StockBench.controllers.export import FolderResultsExporter
from StockBench.constants import *


class FolderOverviewSidebar(OverviewSideBar):
    def __init__(self, progress_observers):
        # pass a summy progress observer to the superclass as we are overriding the
        # update output box function now that we have a list of progress observers
        dummy_progress_observer = ProgressObserver()
        super().__init__(dummy_progress_observer)
        self.simulation_results_to_export = {}

        self.progress_observers = progress_observers

        # add shared_components to the layout
        self.layout.addWidget(self.metadata_header)

        self.metadata_table = MultiMetadataSidebarTable()
        self.layout.addWidget(self.metadata_table)

        self.layout.addWidget(self.export_json_btn)

        self.folder_selection = FolderSelector()
        self.layout.addWidget(self.folder_selection)

        self.layout.addWidget(self.export_excel_btn)
        self.layout.addWidget(self.export_md_btn)

        # pushes the status header and output box to the bottom
        self.layout.addStretch()

        self.layout.addWidget(self.status_header)

        self.layout.addWidget(self.output_box)

        # apply the layout
        self.setLayout(self.layout)

    def on_export_json_btn_clicked(self):
        # make sure that results exist before trying to export
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

            # show a message box indicating results were copied
            self._show_message_box('Export Notification', 'Results copied to clipboard')

    def on_export_excel_btn_clicked(self):
        # make sure that results exist before trying to export
        if self.simulation_results_to_export:
            # get the filepath from the ui component
            folder_path = self.folder_selection.folderpath_box.text()

            # export the data to the xlsx file
            exporter = FolderResultsExporter()
            filepath = exporter.export(self.simulation_results_to_export['results'], folder_path, 'FolderResults')

            # show a message box indicating the file was saved
            self._show_message_box('Export Notification', f'File has been saved to {filepath}')

    def on_export_md_btn_clicked(self):
        """Export simulation results to markdown."""
        if self.simulation_results_to_export:
            filepath = MarkdownExporter.export_folder_simulation_to_md(self.simulation_results_to_export)

            # show a message box indicating results were copied
            self._show_message_box('Export Notification', f'Results exported to {filepath}')

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
        export_dict.pop(ELAPSED_TIME_KEY)
        export_dict.pop(POSITIONS_KEY)

        return export_dict

    def render_data(self, simulation_results: dict):
        # save the results to allow exporting
        self.simulation_results_to_export = simulation_results
        # extract the results list
        results = simulation_results['results']
        # select the first result to use as a template
        result_to_use = results[0]
        # extract the elapsed time and inject it into the result to use (represents the entire sim time)
        result_to_use[ELAPSED_TIME_KEY] = simulation_results[ELAPSED_TIME_KEY]
        self.metadata_table.render_data(result_to_use)
