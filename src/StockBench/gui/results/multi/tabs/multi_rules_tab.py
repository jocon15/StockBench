from StockBench.models.constants.general_constants import BUY_SIDE
from StockBench.gui.results.base.rules_tab import RulesTab
from StockBench.gui.results.multi.constants.constants import BUY_RULES_BAR_CHART_KEY, SELL_RULES_BAR_CHART_KEY


class MultiRulesTab(RulesTab):
    """Tab showing simulation rule analysis for multi-symbol simulation results."""

    def __init__(self, side):
        super().__init__(side)
        self.layout.addWidget(self.html_viewer)

        self.setLayout(self.layout)

    def render_chart(self, chart_filepaths: dict):
        if self.side == BUY_SIDE:
            chart_filepath = chart_filepaths[BUY_RULES_BAR_CHART_KEY]
        else:
            chart_filepath = chart_filepaths[SELL_RULES_BAR_CHART_KEY]

        self.html_viewer.render_data(chart_filepath)
