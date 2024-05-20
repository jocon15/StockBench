from StockBench.display.display import Display
from StockBench.gui.windows.base.results_window import SimulationResultsWindow
from StockBench.gui.windows.singular.tabs.singular_overview_tab import SingularOverviewTab
from StockBench.gui.windows.singular.tabs.singular_rules_tab import SingularRulesTab
from StockBench.gui.windows.base.positions_tab import PositionsTab


class SingularResultsWindow(SimulationResultsWindow):
    """Window that holds the progress bar and the results box for a simulation on a single symbol."""
    def __init__(self, worker, simulator, progress_observer, initial_balance):
        super().__init__(worker, simulator, progress_observer, initial_balance)
        # get set by caller (MainWindow) after construction but before .show()
        self.symbol = None

        # add objects to layout
        # progress bar
        self.layout.addWidget(self.progress_bar)
        # simulation results frame (gets added to layout via tab widget
        self.results_frame = SingularOverviewTab()
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

    def run_simulation(self) -> dict:
        # load the strategy into the simulator
        if self.logging:
            self.simulator.enable_logging()
        if self.reporting:
            self.simulator.enable_reporting()
        self.simulator.load_strategy(self.strategy)
        if self.unique_chart_saving:
            save_option = Display.UNIQUE_SAVE
        else:
            save_option = Display.TEMP_SAVE
        try:
            return self.simulator.run(self.symbol, show_chart=False, save_option=save_option,
                                      progress_observer=self.progress_observer)
        except ValueError as e:
            # pass the error to the simulation results box
            self.results_frame.update_error_message(f'{e}')
            return {}

    def render_updated_data(self, simulation_results: dict):
        self.results_frame.render_data(simulation_results)
        self.buy_rules_tab.render_data(simulation_results)
        self.sell_rules_tab.render_data(simulation_results)
        self.positions_analysis_tab.render_data(simulation_results)
