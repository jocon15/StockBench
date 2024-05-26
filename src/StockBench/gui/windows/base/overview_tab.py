from PyQt6.QtWidgets import QFrame
from StockBench.gui.windows.base.base.tab import Tab
from abc import abstractmethod
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PyQt6.QtCore import QTimer, QThreadPool


class OverviewTab(Tab):
    """Abstract superclass for a simulation results overview tab."""
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
    # SIDE_BAR_STYLESHEET = """border: 1px solid red"""

    OUTPUT_BOX_STYLESHEET = """color: #fff; background-color: #303136; border: 0px; padding: 5px; max-height: 300px;"""

    title_stylesheet = """max-height:45px; color:#FFF;font-size:20px;font-weight:bold;"""

    error_label_style_sheet = """color:#dc143c; margin-top:10px;"""

    def __init__(self, progress_observer):
        super().__init__()
        self.progress_observer = progress_observer

        # Note: this must be declared before everything else so that the thread pool exists before we attempt to use it
        self.threadpool = QThreadPool()

        # define layout type
        self.layout = QVBoxLayout()

        # results title
        self.results_title = QLabel()
        self.results_title.setText('Simulation Results')
        self.results_title.setStyleSheet(self.title_stylesheet)

        # output box (terminal)
        self.output_box = QListWidget()
        self.output_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.output_box.setStyleSheet(self.OUTPUT_BOX_STYLESHEET)

        # self.setStyleSheet(self.SIDE_BAR_STYLESHEET)

        # status
        self.status_title = QLabel()
        self.status_title.setText('Status')
        self.status_title.setStyleSheet(self.title_stylesheet)

        # timer to periodically read from the progress observer and update output box
        self.timer = QTimer()
        # start the timer to update the output box every 100ms
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.__update_output_box)  # noqa
        self.timer.start()

    def update_error_message(self, message):
        """Set the error message in the output box."""
        list_item = QListWidgetItem(message)
        list_item.setForeground(QColor("red"))
        self.output_box.addItem(list_item)

    def __update_output_box(self):
        """Update the output box with messages from the progress observer."""
        if self.progress_observer.is_completed():
            # stop the timer
            self.timer.stop()
        messages = self.progress_observer.get_messages()
        for message in messages:
            self.output_box.addItem(QListWidgetItem(str(message.msg)))
        # scroll the output box to the bottom
        self.output_box.scrollToBottom()

    @abstractmethod
    def render_data(self, simulation_results: dict):
        raise NotImplementedError('You must define an implementation for render_data()!')


class OverviewTable(QFrame):
    """Superclass for a results table frame."""
    TABLE_STYLESHEET = """max-height:200px"""

    numeric_results_stylesheet = """color:#FFF;"""

    def __init__(self):
        super().__init__()

        self.setStyleSheet(self.TABLE_STYLESHEET)

    @abstractmethod
    def render_data(self, simulation_results: dict):
        raise NotImplementedError('You must define an implementation for render_data()!')
