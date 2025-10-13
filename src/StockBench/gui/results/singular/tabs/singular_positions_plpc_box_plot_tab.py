from StockBench.charting.charting_engine import ChartingEngine
from StockBench.charting.singular.singular_charting_engine import SingularChartingEngine
from StockBench.gui.results.base.base.simple_vertical_chart_tab import SimpleVerticalChartTab
from StockBench.constants import POSITIONS_PROFIT_LOSS_PERCENT_BOX_PLOT_CHART_FILEPATH_KEY, POSITIONS_KEY, SYMBOL_KEY


class SingularPositionsBoxPlotTabVertical(SimpleVerticalChartTab):
    """Tab for singular position histogram chart.

    Note: Cannot inherit from ResultsTab because
    """
    CHART_KEY = POSITIONS_PROFIT_LOSS_PERCENT_BOX_PLOT_CHART_FILEPATH_KEY

    def __init__(self):
        super().__init__()

        self.layout.addWidget(self.html_viewer)

        self.setLayout(self.layout)

    def render_chart(self, simulation_results: dict):
        chart_filepath = SingularChartingEngine.build_single_strategy_result_dataset_positions_plpc_box_plot(
            simulation_results[POSITIONS_KEY],
            simulation_results[SYMBOL_KEY], ChartingEngine.TEMP_SAVE)

        self.html_viewer.render_data(chart_filepath)
