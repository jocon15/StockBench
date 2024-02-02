"""
'symbol': self.__symbol,
'elapsed_time': self.__elapsed_time,
'trades_made': len(self.__position_archive),
'effectiveness': self.__analyzer.effectiveness(),
'average_profit_loss': self.__analyzer.avg_profit_loss(),
'total_profit_loss': self.__account.get_profit_loss(),
'account_value': self.__account.get_balance(),
'chart_filepath': chart_filepath
"""

class MultiAnalyzer:
    def __init__(self, results):
        self.__results = results

    def total_trades_made(self):
        total_trades_made = 0
        for result in self.__results:
            total_trades_made += int(result['trades_made'])

        return total_trades_made

    def total_effectiveness(self):
        total_trades = 0.0
        positive_outcome_trades = 0.0
        for result in self.__results:
            total_trades += float(result['trades_made'])
            positive_outcome_trades += float(result['effectiveness']) * float(result['trades_made'])

        try:
            return (positive_outcome_trades / total_trades) * 100
        except ZeroDivisionError:
            return 0.0

    def total_profit_loss(self):
        total_profit_loss = 0.0
        for result in self.__results:
            total_profit_loss += float(result['total_profit_loss'])
        return total_profit_loss
