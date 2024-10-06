from StockBench.gui.results.base.rules_results_tab import RulesResultsTab


class MultiRulesTab(RulesResultsTab):
    """Tab showing simulation rule analysis for multi-symbol simulation results."""
    def __init__(self, side):
        super().__init__(side)
