

class SimulationAnalyzer:
    def __init__(self, _positions: list):
        self.__positions = _positions
        self.__sum_cache = None
        self.__eff_cache = None
        self.__avg_pl_cache = None

    def effectiveness(self) -> float:
        """Calculates the effectiveness of the simulation."""
        # check for cached effectiveness value
        if self.__eff_cache:
            return self.__eff_cache

        _profitable_trade_count = 0
        for _position in self.__positions:
            if _position.lifetime_profit_loss() >= 0:
                _profitable_trade_count += 1

        try:
            _eff = (_profitable_trade_count / len(self.__positions)) * 100.0
        except ZeroDivisionError:
            _eff = 0.0

        # update the cached value
        self.__eff_cache = round(_eff, 3)
        return self.__eff_cache

    def total_pl(self) -> float:
        """Calculates the total profit/loss of the simulation."""
        # check for cached sum value
        if self.__sum_cache:
            return self.__sum_cache

        _sum = 0.0
        for _position in self.__positions:
            _sum += _position.lifetime_profit_loss()

        # update the cached value
        self.__sum_cache = round(_sum, 3)
        return self.__sum_cache

    def avg_pl(self) -> float:
        """Calculates the average profit/loss of the simulation."""
        # check for cached avg pl value
        if self.__avg_pl_cache:
            return self.__avg_pl_cache

        try:
            _avg_pl = self.total_pl() / float(len(self.__positions))
        except ZeroDivisionError:
            _avg_pl = 0.0

        # update the cached value
        self.__avg_pl_cache = round(_avg_pl, 3)
        return self.__avg_pl_cache
