import sys
from StockBench.gui.gui import MainWindow, QApplication


app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()
