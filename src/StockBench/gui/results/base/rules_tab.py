from StockBench.gui.results.base.base.result_tab import ResultsTab


class RulesResultsTab(ResultsTab):
    """Abstract base class for a rules analysis tab."""
    def __init__(self, side):
        super().__init__(f'{side}_rule_analysis_chart_filepath')
        self.layout.addWidget(self.html_viewer)

        # apply the layout
        self.setLayout(self.layout)
