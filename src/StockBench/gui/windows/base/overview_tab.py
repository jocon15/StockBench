import os
from abc import abstractmethod

from PyQt6 import QtCore, QtWebEngineWidgets
from PyQt6.QtWidgets import QFrame, QLabel


class OverviewTab(QFrame):
    """Abstract superclass for an overview tab."""
    LOADING_REL_PATH = os.path.join('resources', 'default', 'chart_loading.html')
    BACKUP_REL_PATH = os.path.join('resources', 'default', 'chart_unavailable.html')

    CHART_KEY = 'overview_chart_filepath'

    def __init__(self):
        super().__init__()
        # define shared attributes here but adding them to layout happens in subclass
        self.webView = QtWebEngineWidgets.QWebEngineView()
        # load blank html file to cover the white screen while the chart loads
        self.render_chart_loading()

    @abstractmethod
    def render_data(self, simulation_results: dict):
        raise NotImplementedError('You must define an implementation for render_data()!')

    @abstractmethod
    def update_error_message(self, message):
        raise NotImplementedError('You must define an implementation for update_data()!')

    def render_chart_loading(self):
        # load the loading html file
        self.webView.load(QtCore.QUrl().fromLocalFile(os.path.abspath(self.LOADING_REL_PATH)))

    def render_chart(self, simulation_results):
        # check the simulation generated a chart
        chart_loaded = False
        if self.CHART_KEY in simulation_results:
            # check the chart exists
            if os.path.isfile(simulation_results[self.CHART_KEY]):
                chart_loaded = True
                self.webView.load(QtCore.QUrl().fromLocalFile(os.path.abspath(simulation_results[self.CHART_KEY])))

        if not chart_loaded:
            # load the default html file
            self.webView.load(QtCore.QUrl().fromLocalFile(os.path.abspath(self.BACKUP_REL_PATH)))


class OverviewTable(QFrame):
    """Superclass for a results table frame."""
    title_stylesheet = """color:#FFF;font-size:20px;font-weight:bold;"""

    numeric_results_stylesheet = """color:#FFF;"""

    error_label_style_sheet = """color:#dc143c;margin-top:10px;"""

    def __init__(self):
        super().__init__()
        self._error_message = ""

        # Note: this is the only label we can abstract here without PyQt stopp responding error
        self.error_message_box = QLabel()
        self.error_message_box.setWordWrap(True)
        self.error_message_box.setStyleSheet(self.error_label_style_sheet)

    @abstractmethod
    def render_data(self, simulation_results: dict):
        raise NotImplementedError('You must define an implementation for render_data()!')

    def update_error_message(self, message):
        self._error_message = message
