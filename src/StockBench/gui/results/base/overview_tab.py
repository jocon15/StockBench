import subprocess
from PyQt6.QtWidgets import QFrame
from StockBench.gui.results.base.base.result_tab import Tab
from StockBench.gui.palette.palette import Palette
from abc import abstractmethod
from PyQt6.QtCore import Qt, QTimer, QThreadPool
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QGridLayout, QPushButton


class OverviewTab(Tab):
    """Abstract base class for a simulation results overview tab."""
    CHART_KEY = 'overview_chart_filepath'

    def __init__(self):
        super().__init__(self.CHART_KEY)

    @abstractmethod
    def render_data(self, simulation_results: dict):
        raise NotImplementedError('You must define an implementation for render_data()!')

    @abstractmethod
    def update_error_message(self, message):
        raise NotImplementedError('You must define an implementation for update_data()!')


class OverviewSideBar(QWidget):
    """Abstract base class for a sidebar widget."""
    OUTPUT_BOX_STYLESHEET = """color: #fff; background-color: #303136; border-radius: 8px;border: 0px; padding: 5px; 
    max-height: 300px;"""

    EXPORT_BTN_STYLESHEET = """background-color: #303134;color:#FFF;border-width:0px;border-radius:10px;height:25px;"""

    HEADER_STYLESHEET = """max-height:45px; color:#FFF;font-size:20px;font-weight:bold;"""

    def __init__(self, progress_observer):
        super().__init__()
        self.progress_observer = progress_observer

        self.simulation_results_to_export = {}

        # Note: this must be declared before everything else so that the thread pool exists before we attempt to use it
        self.threadpool = QThreadPool()

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
        self.export_json_btn.clicked.connect(self.on_export_json_btn_clicked)  # noqa

        # export excel button
        self.export_excel_btn = QPushButton()
        self.export_excel_btn.setText('Export to ClipBoard (excel)')
        self.export_excel_btn.setStyleSheet(self.EXPORT_BTN_STYLESHEET)
        self.export_excel_btn.clicked.connect(self.on_export_excel_btn_clicked)  # noqa

        # output box (terminal)
        self.output_box = QListWidget()
        self.output_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.output_box.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.output_box.setStyleSheet(self.OUTPUT_BOX_STYLESHEET)

        # status header
        self.status_header = QLabel()
        self.status_header.setText('Status')
        self.status_header.setStyleSheet(self.HEADER_STYLESHEET)

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
        if self.simulation_results_to_export:
            # copy and clean the results info
            export_dict = self._remove_extraneous_info(self.simulation_results_to_export)

            self._copy_to_clipboard(str(export_dict))
        # if no results are available yet, nothing gets copied to the clipboard

    def on_export_excel_btn_clicked(self):
        """On click function for exporting to excel button."""
        if self.simulation_results_to_export:
            # copy and clean the results info
            export_dict = self._remove_extraneous_info(self.simulation_results_to_export)

            # format the results for excel use
            export_values = ''
            for key in export_dict.keys():
                export_values += f'{export_dict[key]},'
            # remove last comma from string
            export_values = export_values.rsplit(',', 1)[0]

            self._copy_to_clipboard(export_values)
        # if no results are available yet, nothing gets copied to the clipboard

    @staticmethod
    def _copy_to_clipboard(text: str):
        # copy the dict to the clipboard
        cmd = 'echo ' + text + '|clip'
        return subprocess.check_call(cmd, shell=True)

    @abstractmethod
    def _remove_extraneous_info(self, results: dict) -> dict:
        raise NotImplementedError('You must define an implementation for _remove_extraneous_info()!')

    @abstractmethod
    def render_data(self, simulation_results: dict):
        raise NotImplementedError('You must define an implementation for render_data()!')


class OverviewTable(QFrame):
    """Superclass for a results table frame."""
    TABLE_STYLESHEET = """max-height:200px; background-color: #303136; border-radius:8px;"""

    RESULT_VALUE_STYLESHEET = """color: #fff;"""

    def __init__(self):
        super().__init__()
        # define the layout
        self.layout = QGridLayout()

        # ========================= Shared Metadata ================================
        # strategy label
        self.strategy_label = QLabel()
        self.strategy_label.setText('Strategy')
        self.strategy_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # strategy data label
        self.strategy_data_label = QLabel()
        self.strategy_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        # trade-able days label
        self.trade_able_days_label = QLabel()
        self.trade_able_days_label.setText('Length')
        self.trade_able_days_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # trade-able days data label
        self.trade_able_days_data_label = QLabel()
        self.trade_able_days_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        # elapsed time label
        self.elapsed_time_label = QLabel()
        self.elapsed_time_label.setText('Elapsed Time')
        self.elapsed_time_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # elapsed time data label
        self.elapsed_time_data_label = QLabel()
        self.elapsed_time_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        # ========================= Shared Results ================================
        # trades made label
        self.trades_made_label = QLabel()
        self.trades_made_label.setText('Trades Made')
        self.trades_made_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # trades made data label
        self.trades_made_data_label = QLabel()
        self.trades_made_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        # effectiveness label
        self.effectiveness_label = QLabel()
        self.effectiveness_label.setText('Effectiveness')
        self.effectiveness_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # effectiveness data label
        self.effectiveness_data_label = QLabel()
        self.effectiveness_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        # total P/L label
        self.total_pl_label = QLabel()
        self.total_pl_label.setText('Total P/L')
        self.total_pl_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # total P/L data label
        self.total_pl_data_label = QLabel()
        self.total_pl_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        # average P/L label
        self.average_pl_label = QLabel()
        self.average_pl_label.setText('Average P/L')
        self.average_pl_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # average P/L data label
        self.average_pl_data_label = QLabel()
        self.average_pl_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        # median P/L label
        self.median_pl_label = QLabel()
        self.median_pl_label.setText('Median P/L')
        self.median_pl_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # median data label
        self.median_pl_data_label = QLabel()
        self.median_pl_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        # stddev P/L label
        self.stddev_pl_label = QLabel()
        self.stddev_pl_label.setText('Stddev P/L')
        self.stddev_pl_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # stddev data label
        self.stddev_pl_data_label = QLabel()
        self.stddev_pl_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)
        # =================================================================

        self.setStyleSheet(self.TABLE_STYLESHEET)

    @abstractmethod
    def render_data(self, simulation_results: dict):
        raise NotImplementedError('You must define an implementation for render_data()!')
