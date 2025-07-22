import subprocess
from abc import abstractmethod
from PyQt6.QtCore import Qt, QTimer, QThreadPool
from PyQt6 import QtGui
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QMessageBox
from StockBench.gui.palette.palette import Palette


class OverviewSideBar(QWidget):
    """Abstract base class for a sidebar widget."""

    def __init__(self, progress_observer):
        super().__init__()
        # Note: this must be declared before everything else so that the thread pool exists before we attempt to use it
        self.threadpool = QThreadPool()

        # attributes
        self.progress_observer = progress_observer

        self.simulation_results_to_export = {}

        # define layout type
        self.layout = QVBoxLayout()

        # metadata header
        self.metadata_header = QLabel()
        self.metadata_header.setText('Metadata')
        self.metadata_header.setStyleSheet(Palette.SIDEBAR_HEADER_STYLESHEET)

        # results header
        self.results_header = QLabel()
        self.results_header.setText('Simulation Results')
        self.results_header.setStyleSheet(Palette.SIDEBAR_HEADER_STYLESHEET)

        # export JSON button
        self.export_json_btn = QPushButton()
        self.export_json_btn.setText('Export to Clipboard (JSON)')
        self.export_json_btn.setStyleSheet(Palette.SECONDARY_BTN)
        self.export_json_btn.clicked.connect(self.on_export_json_btn_clicked)  # noqa

        # export excel button
        self.export_excel_btn = QPushButton()
        self.export_excel_btn.setText('Export to Excel (.xlsx)')
        self.export_excel_btn.setStyleSheet(Palette.SECONDARY_BTN)
        self.export_excel_btn.clicked.connect(self.on_export_excel_btn_clicked)  # noqa

        # export markdown button
        self.export_md_btn = QPushButton()
        self.export_md_btn.setText('Export to Markdown (.md)')
        self.export_md_btn.setStyleSheet(Palette.SECONDARY_BTN)
        self.export_md_btn.clicked.connect(self.on_export_md_btn_clicked)  # noqa

        # output box (terminal)
        self.output_box = QListWidget()
        self.output_box.setWordWrap(True)
        self.output_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.output_box.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.output_box.setStyleSheet(Palette.SIDEBAR_OUTPUT_BOX_STYLESHEET)

        # status header
        self.status_header = QLabel()
        self.status_header.setText('Status')
        self.status_header.setStyleSheet(Palette.SIDEBAR_HEADER_STYLESHEET)

        # timer to periodically read from the progress observer and update output box
        self.timer = QTimer()
        # start the timer to update the output box every 100ms
        self.timer.setInterval(100)
        self.timer.timeout.connect(self._update_output_box)  # noqa
        self.timer.start()

    def update_error_message(self, message):
        # handle the passed down error message by adding it to the output box
        list_item = QListWidgetItem(message)
        list_item.setForeground(QColor('red'))
        self.output_box.addItem(list_item)

    def _update_output_box(self):
        """Update the output box with messages from the progress observer."""
        if self.progress_observer.is_analytics_completed():
            # stop the timer
            self.timer.stop()
        messages = self.progress_observer.get_messages()
        for message in messages:
            list_item = QListWidgetItem(str(message.msg))
            if message.levelname == 'WARNING':
                list_item.setForeground(QColor('yellow'))
            else:
                list_item.setForeground(QColor('grey'))
            self.output_box.addItem(list_item)
        # scroll the output box to the bottom
        self.output_box.scrollToBottom()

    def on_export_json_btn_clicked(self):
        """On click function for exporting to JSON button."""
        # make sure that results exist before trying to export
        if self.simulation_results_to_export:
            # copy and clean the results info
            export_dict = self._remove_extraneous_info(self.simulation_results_to_export)

            self._copy_to_clipboard(str(export_dict))

            # show a message box indicating the file was saved
            self._show_message_box('Export Notification', 'Results copied to clipboard')

    @abstractmethod
    def on_export_md_btn_clicked(self):
        raise NotImplementedError('You must define an implementation for on_export_md_btn_clicked()!')

    @staticmethod
    def _copy_to_clipboard(text: str):
        # copy the dict to the clipboard
        cmd = 'echo ' + text + '|clip'
        return subprocess.check_call(cmd, shell=True)

    @staticmethod
    def _show_message_box(title: str, message: str):
        # show a message box indicating the file was saved
        msgbox = QMessageBox()
        msgbox.setWindowIcon(QtGui.QIcon(Palette.CANDLE_ICON))
        msgbox.setText(message)
        msgbox.setWindowTitle(title)
        msgbox.exec()

    @abstractmethod
    def _remove_extraneous_info(self, results: dict) -> dict:
        raise NotImplementedError('You must define an implementation for _remove_extraneous_info()!')

    @abstractmethod
    def render_data(self, simulation_results: dict):
        raise NotImplementedError('You must define an implementation for render_data()!')
