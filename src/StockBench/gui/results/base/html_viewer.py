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

    def __init__(self):
        super().__init__()

        # define the layout type
        self.layout = QVBoxLayout()

        # add shared_components to the layout
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

    def render_data(self, chart_filepath: str):
        """Render the chart created from the simulation."""
        # check the chart exists
        if os.path.isfile(chart_filepath):
            self.web_engine.load(QtCore.QUrl().fromLocalFile(os.path.abspath(chart_filepath)))
        else:
            # load the default html file
            self.web_engine.load(QtCore.QUrl().fromLocalFile(os.path.abspath(self.BACKUP_REL_PATH)))
