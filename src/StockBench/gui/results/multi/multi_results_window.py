from StockBench.charting.charting_engine import ChartingEngine
from StockBench.charting.multi.multi_charting_engine import MultiChartingEngine
from StockBench.constants import BUY_SIDE, SELL_SIDE, MULTI_RESULTS_KEY, INITIAL_ACCOUNT_VALUE_KEY, POSITIONS_KEY, \
    STRATEGY_KEY
from StockBench.gui.models.simulation_results_bundle import SimulationResultsBundle
from StockBench.gui.results.multi.tabs.multi_positions_plpc_box_plot_tab import MultiPositionsBoxPlotTabVertical
from StockBench.gui.results.base.results_window import SimulationResultsWindow
from StockBench.gui.results.multi.tabs.multi_rules_tab import MultiRulesTab
from StockBench.gui.results.multi.tabs.multi_overview_tab import MultiOverviewTab
from StockBench.gui.results.multi.tabs.multi_positions_pl_tab import MultiPositionsProfitLossTabVertical
from StockBench.gui.results.multi.tabs.multi_positions_plpc_histogram_tab import MultiPositionsHistogramTabVertical
from StockBench.gui.results.multi.tabs.multi_positions_duration_tab import MultiPositionsDurationTabVertical
from StockBench.gui.results.multi.constants.constants import *
from StockBench.simulator import Simulator


class MultiResultsWindow(SimulationResultsWindow):
    """Simulation results window for a simulation on multiple symbols."""

    def __init__(self, symbols, strategy, initial_balance, logging_on, reporting_on, unique_chart_saving_on,
                 results_depth, identifier: int = 1):
        super().__init__(strategy, initial_balance, logging_on, reporting_on, unique_chart_saving_on, results_depth,
                         identifier=identifier)
        self.symbols = symbols

        # add shared_components to the layout
        # progress bar
        self.layout.addWidget(self.progress_bar)
        # simulation results frame (gets added to layout via tab widget)
        self.overview_tab = MultiOverviewTab(self.progress_observer)
        # buy and sell rules analysis tabs (gets added to layout via tab widget)
        self.buy_rules_tab = MultiRulesTab(BUY_SIDE)
        self.sell_rules_tab = MultiRulesTab(SELL_SIDE)
        # positions analysis tab (gets added to layout via tab widget)
        self.positions_duration_bar_tab = MultiPositionsDurationTabVertical()
        self.positions_pl_bar_tab = MultiPositionsProfitLossTabVertical()
        self.positions_plpc_histogram_tab = MultiPositionsHistogramTabVertical()
        self.positions_plpc_box_plot_tab = MultiPositionsBoxPlotTabVertical()
        # tab widget
        self.tab_widget.addTab(self.overview_tab, 'Overview')
        self.tab_widget.addTab(self.buy_rules_tab, 'Buy Rules')
        self.tab_widget.addTab(self.sell_rules_tab, 'Sell Rules')
        self.tab_widget.addTab(self.positions_duration_bar_tab, 'Positions Duration (bar)')
        self.tab_widget.addTab(self.positions_pl_bar_tab, 'Positions P/L (bar)')
        self.tab_widget.addTab(self.positions_plpc_histogram_tab, 'Positions P/L % (histogram)')
        self.tab_widget.addTab(self.positions_plpc_box_plot_tab, 'Positions P/L % (box plot)')
        self.layout.addWidget(self.tab_widget)

        # apply the layout to the window
        self.setLayout(self.layout)

    def _run_simulation(self, save_option: int, results_depth: int) -> SimulationResultsBundle:
        """Implementation of running the simulation for multi-symbol simulation."""
        simulation_results = self.simulator.run_multiple(self.symbols, self.progress_observer)

        if results_depth == Simulator.CHARTS_AND_DATA:
            chart_filepaths = {
                OVERVIEW_CHART_FILEPATH: MultiChartingEngine.build_multi_overview_chart(
                    simulation_results[MULTI_RESULTS_KEY], simulation_results[INITIAL_ACCOUNT_VALUE_KEY],
                    ChartingEngine.TEMP_SAVE),
                BUY_RULES_BAR_CHART: ChartingEngine.build_rules_bar_chart(
                    simulation_results[POSITIONS_KEY], BUY_SIDE, None, ChartingEngine.TEMP_SAVE),
                SELL_RULES_BAR_CHART: ChartingEngine.build_rules_bar_chart(
                    simulation_results[POSITIONS_KEY], SELL_SIDE, None, ChartingEngine.TEMP_SAVE),
                POSITIONS_DURATION_BAR_CHART_FILEPATH: ChartingEngine.build_positions_duration_bar_chart(
                    simulation_results[POSITIONS_KEY], None, ChartingEngine.TEMP_SAVE),
                POSITIONS_PL_BAR_CHART_FILEPATH: ChartingEngine.build_positions_profit_loss_bar_chart(
                    simulation_results[POSITIONS_KEY], None, ChartingEngine.TEMP_SAVE),
                POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH:
                    ChartingEngine.build_single_strategy_result_dataset_positions_plpc_histogram_chart(
                        simulation_results[POSITIONS_KEY], simulation_results[STRATEGY_KEY], None,
                        ChartingEngine.TEMP_SAVE),
                POSITIONS_PLPC_BOX_PLOT_CHART_FILEPATH:
                    ChartingEngine.build_single_strategy_result_dataset_positions_plpc_box_plot(
                        simulation_results[POSITIONS_KEY], simulation_results[STRATEGY_KEY], None,
                        ChartingEngine.TEMP_SAVE)
            }
        else:
            # filepaths are set to empty strings which will cause the html viewers to render chart unavailable
            chart_filepaths = {
                OVERVIEW_CHART_FILEPATH: '',
                BUY_RULES_BAR_CHART: '',
                SELL_RULES_BAR_CHART: '',
                POSITIONS_DURATION_BAR_CHART_FILEPATH: '',
                POSITIONS_PL_BAR_CHART_FILEPATH: '',
                POSITIONS_PLPC_HISTOGRAM_CHART_FILEPATH: '',
                POSITIONS_PLPC_BOX_PLOT_CHART_FILEPATH: ''
            }

        return SimulationResultsBundle(simulation_results=simulation_results, chart_filepaths=chart_filepaths)

    def _render_data(self, simulation_results_bundle: SimulationResultsBundle):
        """Render the updated data in the window's shared_components."""
        if simulation_results_bundle.simulation_results.keys():
            self.overview_tab.render_data(simulation_results_bundle)
            self.buy_rules_tab.render_chart(simulation_results_bundle.chart_filepaths)
            self.sell_rules_tab.render_chart(simulation_results_bundle.chart_filepaths)
            self.positions_duration_bar_tab.render_chart(simulation_results_bundle.chart_filepaths)
            self.positions_pl_bar_tab.render_chart(simulation_results_bundle.chart_filepaths)
            self.positions_plpc_histogram_tab.render_chart(simulation_results_bundle.chart_filepaths)
            self.positions_plpc_box_plot_tab.render_chart(simulation_results_bundle.chart_filepaths)
        else:
            # the simulation failed - render the chart unavailable html
            self.overview_tab.html_viewer.render_chart_unavailable()
            self.buy_rules_tab.html_viewer.render_chart_unavailable()
            self.sell_rules_tab.html_viewer.render_chart_unavailable()
            self.positions_duration_bar_tab.html_viewer.render_chart_unavailable()
            self.positions_pl_bar_tab.html_viewer.render_chart_unavailable()
            self.positions_plpc_histogram_tab.html_viewer.render_chart_unavailable()
            self.positions_plpc_box_plot_tab.html_viewer.render_chart_unavailable()
