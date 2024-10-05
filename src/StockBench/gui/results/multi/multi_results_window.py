from StockBench.gui.results.base.results_window import SimulationResultsWindow
from StockBench.gui.results.multi.tabs.multi_rules_tab import MultiRulesTab
from StockBench.gui.results.multi.tabs.multi_overview_tab import MultiOverviewTab
from StockBench.gui.results.base.positions_pl_tab import PositionsProfitLossTab
from StockBench.gui.results.multi.tabs.multi_positions_histogram_tab import MultiPositionsHistogramTab


class MultiResultsWindow(SimulationResultsWindow):
    """Simulation results window for a simulation on multiple symbols."""

    def __init__(self, symbols, strategy, initial_balance, simulator, progress_observer, worker, logging_on, 
                 reporting_on, unique_chart_saving_on, results_depth):
        super().__init__(strategy, initial_balance, simulator, progress_observer, worker, logging_on, reporting_on,
                         unique_chart_saving_on, results_depth)
        self.symbols = symbols

        # add shared_components to the layout
        # progress bar
        self.layout.addWidget(self.progress_bar)
        # simulation results frame (gets added to layout via tab widget)
        self.results_frame = MultiOverviewTab(self.progress_observer)
        # buy and sell rules analysis tabs (gets added to layout via tab widget)
        self.buy_rules_tab = MultiRulesTab('buy')
        self.sell_rules_tab = MultiRulesTab('sell')
        # positions analysis tab (gets added to layout via tab widget)
        self.positions_analysis_tab = PositionsProfitLossTab()
        self.positions_histogram_tab = MultiPositionsHistogramTab()
        # tab widget
        self.tab_widget.addTab(self.results_frame, "Overview")
        self.tab_widget.addTab(self.buy_rules_tab, "Buy Rules")
        self.tab_widget.addTab(self.sell_rules_tab, "Sell Rules")
        self.tab_widget.addTab(self.positions_analysis_tab, 'Positions')
        self.tab_widget.addTab(self.positions_histogram_tab, 'Positions (histogram)')
        self.layout.addWidget(self.tab_widget)

        # apply the layout to the window
        self.setLayout(self.layout)

    def _run_simulation(self, save_option) -> dict:
        """Implementation of running the simulation for multi-symbol simulation."""
        return self.simulator.run_multiple(self.symbols, results_depth=self.results_depth, save_option=save_option,
                                           progress_observer=self.progress_observer)

    def _render_data(self, simulation_results: dict):
        """Render the updated data in the window's shared_components."""
        self.results_frame.render_data(simulation_results)
        self.buy_rules_tab.render_chart(simulation_results)
        self.sell_rules_tab.render_chart(simulation_results)
        self.positions_analysis_tab.render_chart(simulation_results)
        self.positions_histogram_tab.render_data(simulation_results)
