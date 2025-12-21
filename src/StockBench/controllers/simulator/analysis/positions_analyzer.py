import statistics
from functools import lru_cache


class PositionsAnalyzer:
    """This class defines an analyzer object.

    The analyzer object is used to evaluate the positional results of a simulation."""
    ROUNDING_LENGTH = 3

    def __init__(self, positions: list):
        self.__positions = positions

        self.__pl_list = [position.lifetime_profit_loss() for position in self.__positions]
        self.__plpc_list = [position.lifetime_profit_loss_percent() for position in self.__positions]

    def total_trades(self) -> int:
        """Calculates the number of trades made during the simulation."""
        return len(self.__positions)

    @lru_cache(maxsize=None)
    def effectiveness(self) -> float:
        """Calculates effectiveness of the simulation."""
        profitable_trade_count = 0
        for _position in self.__positions:
            if _position.lifetime_profit_loss() >= 0:
                profitable_trade_count += 1

        try:
            effectiveness = (profitable_trade_count / len(self.__positions)) * 100.0
        except ZeroDivisionError:
            effectiveness = 0.0

        return round(effectiveness, PositionsAnalyzer.ROUNDING_LENGTH)

    @lru_cache(maxsize=None)
    def total_pl(self) -> float:
        """Calculates the total profit/loss of the simulation."""
        return round(sum(self.__pl_list), PositionsAnalyzer.ROUNDING_LENGTH)

    @lru_cache(maxsize=None)
    def average_trade_duration(self) -> float:
        """Calculates the average trade duration of the simulation."""
        if self.total_trades() > 0:
            durations_list = [position.duration() for position in self.__positions]
            return round(statistics.mean(durations_list), self.ROUNDING_LENGTH)
        else:
            return 0.0

    @lru_cache(maxsize=None)
    def average_pl(self) -> float:
        """Calculates the average profit/loss of the simulation."""
        if self.total_trades() > 0:
            return round(statistics.mean(self.__pl_list), self.ROUNDING_LENGTH)
        else:
            return 0.0

    @lru_cache(maxsize=None)
    def average_plpc(self) -> float:
        """Calculates average profit/loss percent of the simulation."""
        if self.total_trades() > 0:
            return round(statistics.mean(self.__plpc_list), self.ROUNDING_LENGTH)
        else:
            return 0.0

    @lru_cache(maxsize=None)
    def median_pl(self) -> float:
        """Calculates the average profit/loss of the simulation."""
        if self.total_trades() > 0:
            return round(statistics.median(self.__pl_list), self.ROUNDING_LENGTH)
        else:
            return 0.0

    @lru_cache(maxsize=None)
    def median_plpc(self) -> float:
        """Calculates the median profit/loss percent of the simulation."""
        if self.total_trades() > 0:
            return round(statistics.median(self.__plpc_list), self.ROUNDING_LENGTH)
        else:
            return 0.0

    @lru_cache(maxsize=None)
    def standard_deviation_pl(self) -> float:
        """Calculates the standard deviation (population) profit/loss of the simulation."""
        if self.total_trades() > 0:
            return round(statistics.pstdev(self.__pl_list), self.ROUNDING_LENGTH)
        else:
            return 0.0

    @lru_cache(maxsize=None)
    def standard_deviation_plpc(self) -> float:
        """Calculates the standard deviation (population) profit/loss percent of the simulation."""
        if self.total_trades() > 0:
            return round(statistics.pstdev(self.__plpc_list), self.ROUNDING_LENGTH)
        else:
            return 0.0
