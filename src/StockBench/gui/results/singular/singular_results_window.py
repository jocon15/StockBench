from StockBench.controllers.charting import ChartingEngine
from StockBench.controllers.charting.singular import SingularChartingEngine
from StockBench.gui.models.simulation_results_bundle import SimulationResultsBundle
from StockBench.gui.results.base.results_window import SimulationResultsWindow
from StockBench.gui.results.singular.tabs.singular_overview_tab import SingularOverviewTab
from StockBench.gui.results.singular.tabs.singular_positions_duration_tab import SingularPositionsDurationTabVertical
from StockBench.gui.results.singular.tabs.singular_positions_pl_tab import SingularPositionsProfitLossTabVertical
from StockBench.gui.results.singular.tabs.singular_positions_plpc_box_plot_tab import \
    SingularPositionsBoxPlotTabVertical
from StockBench.gui.results.singular.tabs.singular_positions_plpc_histogram_tab import \
    SingularPositionsHistogramTabVertical
from StockBench.gui.results.singular.tabs.singular_rules_tab import SingularRulesTab
from StockBench.gui.results.singular.tabs.singular_account_value_tab import SingularAccountValueTabVertical
from StockBench.controllers.simulator import Simulator
from StockBench.gui.results.singular.constants.constants import *
from StockBench.constants import *


class SingularResultsWindow(SimulationResultsWindow):
    """Simulation results window for a simulation on a single symbol."""

    def __init__(self, symbol, strategy, initial_balance, logging_on, reporting_on, unique_chart_saving_on, show_volume,
                 results_depth):
        super().__init__(strategy, initial_balance, logging_on, reporting_on, unique_chart_saving_on, show_volume,
                         results_depth)
        self.symbol = symbol

        self.layout.addWidget(self.progress_bar)

        self.overview_tab = SingularOverviewTab(self.progress_observer, show_volume)
        self.buy_rules_tab = SingularRulesTab(BUY_SIDE)
        self.sell_rules_tab = SingularRulesTab(SELL_SIDE)
        self.account_value_bar_tab = SingularAccountValueTabVertical()
        self.positions_duration_bar_tab = SingularPositionsDurationTabVertical()
        self.positions_pl_bar_tab = SingularPositionsProfitLossTabVertical()
        self.positions_plpc_histogram_tab = SingularPositionsHistogramTabVertical()
        self.positions_plpc_box_plot_tab = SingularPositionsBoxPlotTabVertical()

        self.tab_widget.addTab(self.overview_tab, 'Overview')
        self.tab_widget.addTab(self.buy_rules_tab, 'Buy Rules')
        self.tab_widget.addTab(self.sell_rules_tab, 'Sell Rules')
        self.tab_widget.addTab(self.account_value_bar_tab, 'Account Value')
        self.tab_widget.addTab(self.positions_duration_bar_tab, 'Positions Duration (bar)')
        self.tab_widget.addTab(self.positions_pl_bar_tab, 'Positions P/L (bar)')
        self.tab_widget.addTab(self.positions_plpc_histogram_tab, 'Positions P/L % (histogram)')
        self.tab_widget.addTab(self.positions_plpc_box_plot_tab, 'Positions P/L % (box plot)')
        self.layout.addWidget(self.tab_widget)

        self.setLayout(self.layout)

    def _run_simulation(self, save_option: int, results_depth: int) -> SimulationResultsBundle:
        """Implementation of running the simulation for a single symbol simulation on a QThread."""
        simulation_results = self.simulator.run(self.symbol, self.progress_observer)

        if results_depth == Simulator.CHARTS_AND_DATA:
            chart_filepaths = {
                OVERVIEW_CHART_FILEPATH_KEY: SingularChartingEngine.build_singular_overview_chart(
                    simulation_results[NORMALIZED_SIMULATION_DATA], simulation_results[SYMBOL_KEY],
                    simulation_results[AVAILABLE_INDICATORS], self.show_volume, save_option),
                ACCOUNT_VALUE_LINE_CHART_FILEPATH_KEY: SingularChartingEngine.build_account_value_line_chart(
                    simulation_results[NORMALIZED_SIMULATION_DATA][Simulator.ACCOUNT_VALUE_COLUMN_NAME].tolist(),
                    simulation_results[SYMBOL_KEY], save_option),
                BUY_RULES_BAR_CHART_KEY: ChartingEngine.build_rules_bar_chart(
                    simulation_results[POSITIONS_KEY], BUY_SIDE, simulation_results[SYMBOL_KEY], save_option),
                SELL_RULES_BAR_CHART_KEY: ChartingEngine.build_rules_bar_chart(
                    simulation_results[POSITIONS_KEY], SELL_SIDE, simulation_results[SYMBOL_KEY], save_option),
                POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY: ChartingEngine.build_positions_duration_bar_chart(
                    simulation_results[POSITIONS_KEY], simulation_results[SYMBOL_KEY], save_option),
                POSITIONS_PL_BAR_CHART_FILEPATH_KEY: ChartingEngine.build_positions_profit_loss_bar_chart(
                    simulation_results[POSITIONS_KEY], simulation_results[SYMBOL_KEY], save_option),
                POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH_KEY:
                    SingularChartingEngine.build_single_strategy_result_dataset_positions_plpc_histogram_chart(
                        simulation_results[POSITIONS_KEY], simulation_results[SYMBOL_KEY],
                        simulation_results[STRATEGY_KEY], save_option),
                POSITIONS_PLPC_BOX_PLOT_CHART_FILEPATH_KEY:
                    SingularChartingEngine.build_single_strategy_result_dataset_positions_plpc_box_plot(
                        simulation_results[POSITIONS_KEY], simulation_results[STRATEGY_KEY],
                        simulation_results[SYMBOL_KEY], save_option)
            }
        else:
            # filepaths are set to empty strings which will cause the html viewers to render chart unavailable
            chart_filepaths = {
                OVERVIEW_CHART_FILEPATH_KEY: '',
                ACCOUNT_VALUE_LINE_CHART_FILEPATH_KEY: '',
                BUY_RULES_BAR_CHART_KEY: '',
                SELL_RULES_BAR_CHART_KEY: '',
                POSITIONS_DURATION_BAR_CHART_FILEPATH_KEY: '',
                POSITIONS_PL_BAR_CHART_FILEPATH_KEY: '',
                POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH_KEY: '',
                POSITIONS_PLPC_BOX_PLOT_CHART_FILEPATH_KEY: ''
            }

        return SimulationResultsBundle(simulation_results=simulation_results, chart_filepaths=chart_filepaths)

    def _render_data(self, simulation_results_bundle: SimulationResultsBundle):
        """Render the updated data in the window's shared components."""
        if simulation_results_bundle.simulation_results.keys():
            # the simulation succeeded - render the results
            self.overview_tab.render_data(simulation_results_bundle)
            self.buy_rules_tab.render_chart(simulation_results_bundle.chart_filepaths)
            self.sell_rules_tab.render_chart(simulation_results_bundle.chart_filepaths)
            self.account_value_bar_tab.render_chart(simulation_results_bundle.chart_filepaths)
            self.positions_duration_bar_tab.render_chart(simulation_results_bundle.chart_filepaths)
            self.positions_pl_bar_tab.render_chart(simulation_results_bundle.chart_filepaths)
            self.positions_plpc_histogram_tab.render_chart(simulation_results_bundle.chart_filepaths)
            self.positions_plpc_box_plot_tab.render_chart(simulation_results_bundle.chart_filepaths)
        else:
            # the simulation failed - render the chart unavailable html
            self.overview_tab.html_viewer.render_chart_unavailable()
            self.buy_rules_tab.html_viewer.render_chart_unavailable()
            self.sell_rules_tab.html_viewer.render_chart_unavailable()
            self.account_value_bar_tab.html_viewer.render_chart_unavailable()
            self.positions_duration_bar_tab.html_viewer.render_chart_unavailable()
            self.positions_pl_bar_tab.html_viewer.render_chart_unavailable()
            self.positions_plpc_histogram_tab.html_viewer.render_chart_unavailable()
            self.positions_plpc_box_plot_tab.html_viewer.render_chart_unavailable()
