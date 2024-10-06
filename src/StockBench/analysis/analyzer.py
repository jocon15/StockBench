import statistics


class SimulationAnalyzer:
    """This class defines an analyzer object.

    The analyzer object is used to evaluate the positional results of a simulation."""
    rounding_length = 3

    def __init__(self, positions: list):
        self.__positions = positions

        # extract the profit/loss of each position into a list, so we only have to do it once
        self.__profit_loss_list = [position.lifetime_profit_loss() for position in self.__positions]

        self.__sum_cache = None
        self.__effectiveness_cache = None
        self.__average_trade_duration_cache = None
        self.__average_profit_loss_cache = None
        self.__median_profit_loss_cache = None
        self.__standard_profit_loss_deviation_cache = None

    def total_trades(self) -> int:
        """Calculates the number of trades made during the simulation.

        return:
            int: The number of trades made.
        """
        return len(self.__positions)

    def effectiveness(self) -> float:
        """Calculates the effectiveness of the simulation.

        return:
            float: The effectiveness percentage.
        """
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
            self.__effectiveness_cache = round(effectiveness, SimulationAnalyzer.rounding_length)
        return self.__effectiveness_cache

    def total_profit_loss(self) -> float:
        """Calculates the total profit/loss of the simulation.

        return:
            float: The total profit/loss.
        """
        # check for cached sum value
        if not self.__sum_cache:
            # update the cached value
            self.__sum_cache = round(sum(self.__profit_loss_list), SimulationAnalyzer.rounding_length)
        return self.__sum_cache

    def average_trade_duration(self) -> float:
        """Calculates the average trade duration of the simulation.

        return:
            float: The average duration.
        """
        # check for cached avg duration value
        if not self.__average_trade_duration_cache:
            # update the cached value
            if self.total_trades() > 0:
                durations_list = [position.duration() for position in self.__positions]
                self.__average_trade_duration_cache = round(statistics.mean(durations_list),
                                                            SimulationAnalyzer.rounding_length)
            else:
                self.__average_trade_duration_cache = 0.0
        return self.__average_trade_duration_cache

    def average_profit_loss(self) -> float:
        """Calculates the average profit/loss of the simulation.

        return:
            float: The average profit/loss.
        """
        # check for cached avg pl value
        if not self.__average_profit_loss_cache:
            # update the cached value
            if self.total_trades() > 0:
                self.__average_profit_loss_cache = round(statistics.mean(self.__profit_loss_list),
                                                         SimulationAnalyzer.rounding_length)
            else:
                self.__average_profit_loss_cache = 0.0
        return self.__average_profit_loss_cache

    def median_profit_loss(self) -> float:
        """Calculates the average profit/loss of the simulation.

        return:
            float: The average profit/loss.
        """
        # check for cached median pl value
        if not self.__median_profit_loss_cache:
            # update the cached value
            if self.total_trades() > 0:
                self.__median_profit_loss_cache = round(statistics.median(self.__profit_loss_list),
                                                        SimulationAnalyzer.rounding_length)
            else:
                self.__median_profit_loss_cache = 0.0
        return self.__median_profit_loss_cache

    def standard_profit_loss_deviation(self) -> float:
        """Calculates the standard deviation profit/loss of the simulation.

        return:
            float: The standard profit/loss deviation (population).
        """
        if not self.__standard_profit_loss_deviation_cache:
            # update the cached value
            if self.total_trades() > 0:
                self.__standard_profit_loss_deviation_cache = round(statistics.pstdev(self.__profit_loss_list),
                                                                    SimulationAnalyzer.rounding_length)
            else:
                self.__standard_profit_loss_deviation_cache = 0.0
        return self.__standard_profit_loss_deviation_cache
