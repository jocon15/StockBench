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

        self.__sum_cache = None
        self.__effectiveness_cache = None
        self.__average_trade_duration_cache = None
        self.__average_pl_cache = None
        self.__median_pl_cache = None
        self.__standard_pl_deviation_cache = None

    def total_trades(self) -> int:
        """Calculates the number of trades made during the simulation."""
        return len(self.__positions)

    def effectiveness(self) -> float:
        """Calculates effectiveness of the simulation."""
        # check for cached effectiveness value
        if not self.__effectiveness_cache:
            profitable_trade_count = 0
            for _position in self.__positions:
                if _position.lifetime_profit_loss() >= 0:
                    profitable_trade_count += 1

            try:
                effectiveness = (profitable_trade_count / len(self.__positions)) * 100.0
            except ZeroDivisionError:
                effectiveness = 0.0

            # update the cached value
            self.__effectiveness_cache = round(effectiveness, PositionsAnalyzer.ROUNDING_LENGTH)
        return self.__effectiveness_cache

    def total_pl(self) -> float:
        """Calculates the total profit/loss of the simulation."""
        # check for cached sum value
        if not self.__sum_cache:
            # update the cached value
            self.__sum_cache = round(sum(self.__pl_list), PositionsAnalyzer.ROUNDING_LENGTH)
        return self.__sum_cache

    def average_trade_duration(self) -> float:
        """Calculates the average trade duration of the simulation."""
        # check for cached avg duration value
        if not self.__average_trade_duration_cache:
            # update the cached value
            if self.total_trades() > 0:
                durations_list = [position.duration() for position in self.__positions]
                self.__average_trade_duration_cache = round(statistics.mean(durations_list), self.ROUNDING_LENGTH)
            else:
                self.__average_trade_duration_cache = 0.0
        return self.__average_trade_duration_cache

    def average_pl(self) -> float:
        """Calculates the average profit/loss of the simulation."""
        if not self.__average_pl_cache:
            if self.total_trades() > 0:
                self.__average_pl_cache = round(statistics.mean(self.__pl_list), self.ROUNDING_LENGTH)
            else:
                self.__average_pl_cache = 0.0
        return self.__average_pl_cache

    @lru_cache(maxsize=None)
    def average_plpc(self) -> float:
        """Calculates average profit/loss percent of the simulation."""
        if self.total_trades() > 0:
            return round(statistics.mean(self.__plpc_list), self.ROUNDING_LENGTH)
        else:
            return 0.0

    def median_pl(self) -> float:
        """Calculates the average profit/loss of the simulation."""
        if not self.__median_pl_cache:
            if self.total_trades() > 0:
                self.__median_pl_cache = round(statistics.median(self.__pl_list), self.ROUNDING_LENGTH)
            else:
                self.__median_pl_cache = 0.0
        return self.__median_pl_cache

    @lru_cache(maxsize=None)
    def median_plpc(self) -> float:
        """Calculates the median profit/loss percent of the simulation."""
        if self.total_trades() > 0:
            return round(statistics.median(self.__plpc_list), self.ROUNDING_LENGTH)
        else:
            return 0.0

    def standard_deviation_pl(self) -> float:
        """Calculates the standard deviation (population) profit/loss of the simulation."""
        if not self.__standard_pl_deviation_cache:
            if self.total_trades() > 0:
                self.__standard_pl_deviation_cache = round(statistics.pstdev(self.__pl_list), self.ROUNDING_LENGTH)
            else:
                self.__standard_pl_deviation_cache = 0.0
        return self.__standard_pl_deviation_cache

    @lru_cache(maxsize=None)
    def standard_deviation_plpc(self) -> float:
        """Calculates the standard deviation (population) profit/loss percent of the simulation."""
        if self.total_trades() > 0:
            return round(statistics.pstdev(self.__plpc_list), self.ROUNDING_LENGTH)
        else:
            return 0.0