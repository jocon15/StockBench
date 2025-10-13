from StockBench.charting.charting_engine import ChartingEngine
from StockBench.charting.singular.singular_charting_engine import SingularChartingEngine
from StockBench.gui.results.base.base.simple_vertical_chart_tab import SimpleVerticalChartTab
from StockBench.constants import POSITIONS_PROFIT_LOSS_BAR_CHART_FILEPATH_KEY, SYMBOL_KEY, POSITIONS_KEY


class SingularPositionsProfitLossTabVertical(SimpleVerticalChartTab):
    """Generic positions analysis tab."""
    CHART_KEY = POSITIONS_PROFIT_LOSS_BAR_CHART_FILEPATH_KEY

    def __init__(self):
        super().__init__()

        self.layout.addWidget(self.html_viewer)

        self.setLayout(self.layout)

    def render_chart(self, simulation_results):
        charting_engine = ChartingEngine.build_positions_profit_loss_bar_chart(
            simulation_results[POSITIONS_KEY],
            simulation_results[SYMBOL_KEY], ChartingEngine.TEMP_SAVE)

        self.html_viewer.render_data(charting_engine)
