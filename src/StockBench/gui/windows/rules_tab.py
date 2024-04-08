
from PyQt6.QtWidgets import QWidget, QVBoxLayout


class RulesTab(QWidget):
    """Superclass for a rules analysis tab."""
    def __init__(self, side):
        super().__init__()

        self.side = side

        self.layout = QVBoxLayout()
