from StockBench.gui.windows.base.base.tab import Tab


class PositionsTab(Tab):
    """Abstract base class for a positions analysis tab."""
    CHART_KEY = 'position_analysis_chart_filepath'

    def __init__(self):
        super().__init__(self.CHART_KEY)

        self.layout.addWidget(self.html_viewer)

        # apply the layout
        self.setLayout(self.layout)
