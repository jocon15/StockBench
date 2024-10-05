from StockBench.gui.results.base.base.result_tab import RulesTab


class RulesResultsTab(RulesTab):
    """Abstract base class for a rules analysis tab."""
    def __init__(self, side):
        super().__init__(side)
        self.layout.addWidget(self.html_viewer)

        # apply the layout
        self.setLayout(self.layout)
