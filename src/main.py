import sys
from PyQt6.QtWidgets import QApplication
from StockBench.gui.gui import ConfigMainWindow


app = QApplication(sys.argv)
window = ConfigMainWindow()
window.show()

app.exec()
