from StockBench.gui.windows.base.base.tab import Tab


class RulesTab(Tab):
    """Abstract superclass for a rules analysis tab."""

    def __init__(self, side):
        super().__init__(f'{side}_rule_analysis_chart_filepath')
        self.layout.addWidget(self.webView)

        # apply the layout
        self.setLayout(self.layout)
