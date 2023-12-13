import sys
from PyQt6.QtWidgets import QApplication
from StockBench.gui.gui import MainWindow


app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()
