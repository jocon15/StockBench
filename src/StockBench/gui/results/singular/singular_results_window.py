from StockBench.gui.results.base.results_window import SimulationResultsWindow
from StockBench.gui.results.singular.tabs.singular_overview_tab import SingularOverviewTab
from StockBench.gui.results.singular.tabs.singular_rules_tab import SingularRulesTab
from StockBench.gui.results.base.positions_tab import PositionsTab


class SingularResultsWindow(SimulationResultsWindow):
    """Simulation results window for a simulation on a single symbol."""

    def __init__(self, symbol, strategy, initial_balance, simulator, progress_observer, worker, logging_on,
                 reporting_on, unique_chart_saving_on, results_depth):
        super().__init__(strategy, initial_balance, simulator, progress_observer, worker, logging_on, reporting_on,
                         unique_chart_saving_on, results_depth)
        self.symbol = symbol

        # add shared_components to the layout
        # progress bar
        self.layout.addWidget(self.progress_bar)
        # simulation results frame (gets added to layout via tab widget
        self.results_frame = SingularOverviewTab(self.progress_observer)
        # buy and sell rules analysis tabs (gets added to layout via tab widget)
        self.buy_rules_tab = SingularRulesTab('buy')
        self.sell_rules_tab = SingularRulesTab('sell')
        # positions analysis tab (gets added to layout via tab widget)
        self.positions_analysis_tab = PositionsTab()
        # tab widget
        self.tab_widget.addTab(self.results_frame, 'Overview')
        self.tab_widget.addTab(self.buy_rules_tab, 'Buy Rules (beta)')
        self.tab_widget.addTab(self.sell_rules_tab, 'Sell Rules (beta)')
        self.tab_widget.addTab(self.positions_analysis_tab, 'Positions')
        self.layout.addWidget(self.tab_widget)

        # apply the layout to the window
        self.setLayout(self.layout)

    def _run_simulation(self, save_option) -> dict:
        """Implementation of running the simulation for a single symbol simulation."""
        return self.simulator.run(self.symbol, results_depth=self.results_depth, save_option=save_option,
                                  progress_observer=self.progress_observer)

    def _render_data(self, simulation_results: dict):
        """Render the updated data in the window's shared_components."""
        self.results_frame.render_data(simulation_results)
        self.buy_rules_tab.render_chart(simulation_results)
        self.sell_rules_tab.render_chart(simulation_results)
        self.positions_analysis_tab.render_chart(simulation_results)
