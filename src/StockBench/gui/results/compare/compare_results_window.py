from PyQt6.QtWidgets import QWidget, QHBoxLayout
from StockBench.gui.palette.palette import Palette
from StockBench.gui.results.multi.multi_results_window import MultiResultsWindow


class CompareResultsWindow(QWidget):
    def __init__(self, simulation1: MultiResultsWindow, simulation2: MultiResultsWindow):
        super().__init__()
        self.setWindowTitle('Simulation Results')
        self.setStyleSheet(Palette.WINDOW_STYLESHEET)

        self.layout = QHBoxLayout()

        self.simulation_widget_1 = simulation1
        self.simulation_widget_1.begin()

        self.simulation_widget_2 = simulation2
        self.simulation_widget_2.begin()

        self.layout.addWidget(self.simulation_widget_1)
        self.layout.addWidget(self.simulation_widget_2)

        self.setLayout(self.layout)
