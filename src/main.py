import sys
from PyQt6.QtWidgets import QApplication
from StockBench.gui.gui import ConfigMainWindow


def main():
    app = QApplication(sys.argv)
    window = ConfigMainWindow()
    window.show()

    app.exec()


if __name__ == '__main__':
    main()
