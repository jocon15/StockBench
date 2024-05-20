import os
from PyQt6 import QtCore, QtWebEngineWidgets
from PyQt6.QtWidgets import QWidget, QVBoxLayout


class PositionsTab(QWidget):
    """Abstract superclass for a positions analysis tab."""
    LOADING_REL_PATH = os.path.join('resources', 'default', 'chart_loading.html')
    BACKUP_REL_PATH = os.path.join('resources', 'default', 'chart_unavailable.html')

    CHART_KEY = 'position_analysis_chart_filepath'

    def __init__(self):
        super().__init__()
        # layout type
        self.layout = QVBoxLayout()

        # add objects to the layout
        self.webView = QtWebEngineWidgets.QWebEngineView()
        self.layout.addWidget(self.webView)

        # apply the layout
        self.setLayout(self.layout)

        # load blank html file to cover the white screen while the chart loads
        self.render_chart_loading()

    def render_chart_loading(self):
        # load the loading html file
        self.webView.load(QtCore.QUrl().fromLocalFile(os.path.abspath(self.LOADING_REL_PATH)))

    def render_data(self, simulation_results):
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
