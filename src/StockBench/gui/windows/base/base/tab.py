import os
from PyQt6 import QtCore, QtWebEngineWidgets
from PyQt6.QtWidgets import QFrame, QHBoxLayout


class Tab(QFrame):
    """Abstract superclass for a simulation results overview tab."""
    LOADING_REL_PATH = os.path.join('resources', 'default', 'chart_loading.html')
    BACKUP_REL_PATH = os.path.join('resources', 'default', 'chart_unavailable.html')

    def __init__(self, chart_key):
        super().__init__()
        self.chart_key = chart_key

        # layout type
        self.layout = QHBoxLayout()

        self.webView = QtWebEngineWidgets.QWebEngineView()

        # load blank html file to cover the white screen while the chart loads
        self.render_chart_loading()

    def render_chart_loading(self):
        # load the loading html file
        self.webView.load(QtCore.QUrl().fromLocalFile(os.path.abspath(self.LOADING_REL_PATH)))

    def render_chart(self, simulation_results):
        # check the simulation generated a chart
        chart_loaded = False
        if self.chart_key in simulation_results:
            # check the chart exists
            if os.path.isfile(simulation_results[self.chart_key]):
                chart_loaded = True
                self.webView.load(QtCore.QUrl().fromLocalFile(os.path.abspath(simulation_results[self.chart_key])))

        if not chart_loaded:
            # load the default html file
            self.webView.load(QtCore.QUrl().fromLocalFile(os.path.abspath(self.BACKUP_REL_PATH)))
