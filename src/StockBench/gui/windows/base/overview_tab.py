from PyQt6.QtWidgets import QFrame
from StockBench.gui.windows.base.base.tab import Tab
from abc import abstractmethod
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QGridLayout
from PyQt6.QtCore import QTimer, QThreadPool


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

    HEADER_STYLESHEET = """max-height:45px; color:#FFF;font-size:20px;font-weight:bold;"""

    def __init__(self, progress_observer):
        super().__init__()
        self.progress_observer = progress_observer

        # Note: this must be declared before everything else so that the thread pool exists before we attempt to use it
        self.threadpool = QThreadPool()

        # define layout type
        self.layout = QVBoxLayout()

        # results header
        self.results_header = QLabel()
        self.results_header.setText('Simulation Results')
        self.results_header.setStyleSheet(self.HEADER_STYLESHEET)

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
            list_item.setForeground(QColor('grey'))
            self.output_box.addItem(list_item)
        # scroll the output box to the bottom
        self.output_box.scrollToBottom()

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

        self.setStyleSheet(self.TABLE_STYLESHEET)

    @abstractmethod
    def render_data(self, simulation_results: dict):
        raise NotImplementedError('You must define an implementation for render_data()!')
