from StockBench.charting.charting_engine import ChartingEngine
from StockBench.gui.results.base.base.simple_vertical_chart_tab import SimpleVerticalChartTab
from StockBench.constants import POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY, POSITIONS_KEY


class MultiPositionsDurationTabVertical(SimpleVerticalChartTab):
    """Abstract base class for a positions analysis tab."""
    CHART_KEY = POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY

    def __init__(self):
        super().__init__()

        self.layout.addWidget(self.html_viewer)

        self.setLayout(self.layout)

    def render_chart(self, simulation_results: dict):
        chart_filepath = ChartingEngine.build_positions_duration_bar_chart(
            simulation_results[POSITIONS_KEY],
            None,
            ChartingEngine.TEMP_SAVE)

        self.html_viewer.render_data(chart_filepath)
