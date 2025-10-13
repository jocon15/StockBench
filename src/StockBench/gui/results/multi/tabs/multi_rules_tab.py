from StockBench.charting.charting_engine import ChartingEngine
from StockBench.constants import POSITIONS_KEY
from StockBench.gui.results.base.rules_tab import RulesTab


class MultiRulesTab(RulesTab):
    """Tab showing simulation rule analysis for multi-symbol simulation results."""

    def __init__(self, side):
        super().__init__(side)
        self.layout.addWidget(self.html_viewer)

        self.setLayout(self.layout)

    def render_chart(self, simulation_results: dict):
        chart_filepath = ChartingEngine.build_rules_bar_chart(
            simulation_results[POSITIONS_KEY],
            self.side,
            None,
            ChartingEngine.TEMP_SAVE)

        self.html_viewer.render_data(chart_filepath)
