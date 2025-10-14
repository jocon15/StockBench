from StockBench.constants import BUY_SIDE
from StockBench.gui.results.base.rules_tab import RulesTab
from StockBench.gui.results.singular.constants.constants import BUY_RULES_BAR_CHART, SELL_RULES_BAR_CHART


class SingularRulesTab(RulesTab):
    """Tab showing simulation rule analysis for single-symbol simulation results."""

    def __init__(self, side):
        super().__init__(side)
        self.layout.addWidget(self.html_viewer)

        self.setLayout(self.layout)

    def render_chart(self, chart_filepaths: dict):
        if self.side == BUY_SIDE:
            chart_filepath = chart_filepaths[BUY_RULES_BAR_CHART]
        else:
            chart_filepath = chart_filepaths[SELL_RULES_BAR_CHART]

        self.html_viewer.render_data(chart_filepath)
