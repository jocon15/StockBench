class SimulationAnalyzer:
    """This class defines an analyzer object.

    The analyzer object is used to evaluate the positional results of a simulation."""
    def __init__(self, positions: list):
        self.__positions = positions
        self.__sum_cache = None
        self.__effectiveness_cache = None
        self.__average_profit_loss_cache = None

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
            profit_loss_sum = 0.0
            for position in self.__positions:
                profit_loss_sum += position.lifetime_profit_loss()

            # update the cached value
            self.__sum_cache = round(profit_loss_sum, 3)
        return self.__sum_cache

    def avg_profit_loss(self) -> float:
        """Calculates the average profit/loss of the simulation.

        return:
            float: The average profit/loss.
        """
        # check for cached avg pl value
        if not self.__average_profit_loss_cache:
            try:
                average_profit_loss = self.total_profit_loss() / float(len(self.__positions))
            except ZeroDivisionError:
                average_profit_loss = 0.0

            # update the cached value
            self.__average_profit_loss_cache = round(average_profit_loss, 3)
        return self.__average_profit_loss_cache
