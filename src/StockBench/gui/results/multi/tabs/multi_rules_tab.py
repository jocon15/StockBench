from StockBench.gui.results.base.rules_tab import RulesTab


class MultiRulesTab(RulesTab):
    """Tab showing simulation rule analysis for multi-symbol simulation results."""
    def __init__(self, side):
        super().__init__(side)
