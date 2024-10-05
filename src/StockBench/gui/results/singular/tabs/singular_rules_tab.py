from StockBench.gui.results.base.rules_results_tab import RulesResultsTab


class SingularRulesTab(RulesResultsTab):
    """Tab showing simulation rule analysis for single-symbol simulation results."""
    def __init__(self, side):
        super().__init__(side)
