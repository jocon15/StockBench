from abc import abstractmethod
from PyQt6.QtWidgets import QFrame, QLabel
from StockBench.gui.windows.base.base.tab import Tab


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
