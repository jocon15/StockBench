from StockBench.controllers.stockbench_controller import StockBenchController
from StockBench.models.constants.general_constants import BUY_SIDE, SELL_SIDE
from StockBench.gui.results.multi.tabs.multi_positions_plpc_box_plot_tab import MultiPositionsBoxPlotTabVertical
from StockBench.gui.results.base.results_window import SimulationResultsWindow
from StockBench.gui.results.multi.tabs.multi_rules_tab import MultiRulesTab
from StockBench.gui.results.multi.tabs.multi_overview_tab import MultiOverviewTab
from StockBench.gui.results.multi.tabs.multi_positions_pl_tab import MultiPositionsProfitLossTabVertical
from StockBench.gui.results.multi.tabs.multi_positions_plpc_histogram_tab import MultiPositionsHistogramTabVertical
from StockBench.gui.results.multi.tabs.multi_positions_duration_tab import MultiPositionsDurationTabVertical
from StockBench.models.simulation_result.simulation_result import SimulationResult


class MultiResultsWindow(SimulationResultsWindow):
    """Simulation results window for a simulation on multiple symbols."""

    def __init__(self, stockbench_controller: StockBenchController, symbols, strategy, initial_balance, logging_on,
                 reporting_on, unique_chart_saving_on, results_depth, identifier):
        super().__init__(stockbench_controller, strategy, initial_balance, logging_on, reporting_on,
                         unique_chart_saving_on, False, results_depth, identifier)
        self.symbols = symbols

        self.layout.addWidget(self.progress_bar)

        self.overview_tab = MultiOverviewTab(self.progress_observer)
        self.buy_rules_tab = MultiRulesTab(BUY_SIDE)
        self.sell_rules_tab = MultiRulesTab(SELL_SIDE)
        self.positions_duration_bar_tab = MultiPositionsDurationTabVertical()
        self.positions_pl_bar_tab = MultiPositionsProfitLossTabVertical()
        self.positions_plpc_histogram_tab = MultiPositionsHistogramTabVertical()
        self.positions_plpc_box_plot_tab = MultiPositionsBoxPlotTabVertical()

        self.tab_widget.addTab(self.overview_tab, 'Overview')
        self.tab_widget.addTab(self.buy_rules_tab, 'Buy Rules')
        self.tab_widget.addTab(self.sell_rules_tab, 'Sell Rules')
        self.tab_widget.addTab(self.positions_duration_bar_tab, 'Positions Duration (bar)')
        self.tab_widget.addTab(self.positions_pl_bar_tab, 'Positions P/L (bar)')
        self.tab_widget.addTab(self.positions_plpc_histogram_tab, 'Positions P/L % (histogram)')
        self.tab_widget.addTab(self.positions_plpc_box_plot_tab, 'Positions P/L % (box plot)')
        self.layout.addWidget(self.tab_widget)

        self.setLayout(self.layout)

    def _run_simulation(self) -> SimulationResult:
        """Implementation of running the simulation for multi-symbol simulation."""
        return self._stockbench_controller.multi_simulation(self.strategy, self.symbols, self.initial_balance,
                                                            self.logging, self.reporting, self.unique_chart_saving,
                                                            self.results_depth, self.progress_observer)

    def _render_data(self, simulation_result: SimulationResult):
        """Render the updated data in the window's shared_components."""
        if simulation_result.simulation_results.keys():
            self.overview_tab.render_data(simulation_result)
            self.buy_rules_tab.render_chart(simulation_result.chart_filepaths)
            self.sell_rules_tab.render_chart(simulation_result.chart_filepaths)
            self.positions_duration_bar_tab.render_chart(simulation_result.chart_filepaths)
            self.positions_pl_bar_tab.render_chart(simulation_result.chart_filepaths)
            self.positions_plpc_histogram_tab.render_chart(simulation_result.chart_filepaths)
            self.positions_plpc_box_plot_tab.render_chart(simulation_result.chart_filepaths)
        else:
            # the simulation failed - render the chart unavailable html
            self.overview_tab.html_viewer.render_chart_unavailable()
            self.buy_rules_tab.html_viewer.render_chart_unavailable()
            self.sell_rules_tab.html_viewer.render_chart_unavailable()
            self.positions_duration_bar_tab.html_viewer.render_chart_unavailable()
            self.positions_pl_bar_tab.html_viewer.render_chart_unavailable()
            self.positions_plpc_histogram_tab.html_viewer.render_chart_unavailable()
            self.positions_plpc_box_plot_tab.html_viewer.render_chart_unavailable()
