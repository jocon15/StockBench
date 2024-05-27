import os
from PyQt6 import QtCore, QtWebEngineWidgets
from PyQt6.QtWidgets import QFrame, QVBoxLayout


class HTMLViewer(QFrame):
    """This class wraps a QWebEngineView widget inside a QFrame.

    QWebEngineView does not have the style abilities of a normal QWidget. To work around this limitation, this class
    wraps the QWebEngineView widget which allows us to access the styles of a normal QWidget.
    """
    LOADING_REL_PATH = os.path.join('resources', 'default', 'chart_loading.html')
    BACKUP_REL_PATH = os.path.join('resources', 'default', 'chart_unavailable.html')

    HTML_VIEWER_STYLESHEET = """margin: 8px; border: 5px solid #111111; border-radius: 10px; 
    background-color: #111111;"""

    def __init__(self, chart_key):
        super().__init__()
        self.chart_key = chart_key

        # define the layout type
        self.layout = QVBoxLayout()

        # add objects to the layout
        self.web_engine = QtWebEngineWidgets.QWebEngineView()
        self.layout.addWidget(self.web_engine)

        # apply the layout
        # self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # apply the stylesheet
        self.setStyleSheet(self.HTML_VIEWER_STYLESHEET)

        # load blank html file to cover the white screen while the chart loads
        self.render_chart_loading()

    def render_chart_loading(self):
        """Render the chart-loading file."""
        self.web_engine.load(QtCore.QUrl().fromLocalFile(os.path.abspath(self.LOADING_REL_PATH)))

    def render_chart(self, simulation_results):
        """Render the chart created from the simulation."""
        # check the simulation generated a chart
        chart_loaded = False
        if self.chart_key in simulation_results:
            # check the chart exists
            if os.path.isfile(simulation_results[self.chart_key]):
                chart_loaded = True
                self.web_engine.load(QtCore.QUrl().fromLocalFile(os.path.abspath(simulation_results[self.chart_key])))

        if not chart_loaded:
            # load the default html file
            self.web_engine.load(QtCore.QUrl().fromLocalFile(os.path.abspath(self.BACKUP_REL_PATH)))
