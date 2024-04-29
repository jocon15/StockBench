from StockBench.gui.windows.rules_tab import RulesTab


class SingularRulesTab(RulesTab):
    def __init__(self, side):
        super().__init__(side)

        self.layout.addWidget(self.webView)

        self.setLayout(self.layout)
