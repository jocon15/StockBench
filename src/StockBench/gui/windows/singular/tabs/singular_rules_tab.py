from StockBench.gui.windows.base.rules_tab import RulesTab


class SingularRulesTab(RulesTab):
    """Tab showing simulation rule analysis for single-symbol simulation results."""
    def __init__(self, side):
        super().__init__(side)

        # add objects to layout
        self.layout.addWidget(self.webView)

        # apply layout
        self.setLayout(self.layout)
