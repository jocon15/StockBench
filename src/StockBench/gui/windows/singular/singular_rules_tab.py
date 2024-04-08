from PyQt6.QtWidgets import QLabel

from StockBench.gui.windows.rules_tab import RulesTab


class SingularRulesTab(RulesTab):
    def __init__(self, side):
        super().__init__(side)

        self.label = QLabel()
        self.label.setText(f'Singular rule results for side: {self.side}')
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)
