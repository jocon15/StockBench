import statistics


class SimulationAnalyzer:
    """This class defines an analyzer object.

    The analyzer object is used to evaluate the positional results of a simulation."""
    def __init__(self, positions: list):
        self.__positions = positions

        # extract the profit/loss of each position into a list, so we only have to do it once
        self.__profit_loss_list = []
        for position in self.__positions:
            self.__profit_loss_list.append(position.lifetime_profit_loss())

        self.__sum_cache = None
        self.__effectiveness_cache = None
        self.__average_profit_loss_cache = None
        self.__standard_profit_loss_deviation_cache = None

    def total_trades(self) -> int:
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
            self.__effectiveness_cache = round(effectiveness, 3)
        return self.__effectiveness_cache

    def total_profit_loss(self) -> float:
        """Calculates the total profit/loss of the simulation.

        return:
            float: The total profit/loss.
        """
        # check for cached sum value
        if not self.__sum_cache:
            # update the cached value
            self.__sum_cache = round(sum(self.__profit_loss_list), 3)
        return self.__sum_cache

    def average_profit_loss(self) -> float:
        """Calculates the average profit/loss of the simulation.

        return:
            float: The average profit/loss.
        """
        # check for cached avg pl value
        if not self.__average_profit_loss_cache:
            # update the cached value
            if self.total_trades() > 0:
                self.__average_profit_loss_cache = round(statistics.mean(self.__profit_loss_list), 3)
            else:
                self.__average_profit_loss_cache = 0.0
        return self.__average_profit_loss_cache

    def standard_profit_loss_deviation(self) -> float:
        """Calculates the standard deviation profit/loss of the simulation.

        return:
            float: The standard profit/loss deviation (population).
        """
        if not self.__standard_profit_loss_deviation_cache:
            # update the cached value
            if self.total_trades() > 0:
                self.__standard_profit_loss_deviation_cache = statistics.pstdev(self.__profit_loss_list)
            else:
                self.__standard_profit_loss_deviation_cache = 0.0
        return self.__standard_profit_loss_deviation_cache
