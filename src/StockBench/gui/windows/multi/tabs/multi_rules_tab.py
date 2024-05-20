from StockBench.gui.windows.base.rules_tab import RulesTab


class MultiRulesTab(RulesTab):
    def __init__(self, side):
        super().__init__(side)

        self.layout.addWidget(self.webView)

        self.setLayout(self.layout)
