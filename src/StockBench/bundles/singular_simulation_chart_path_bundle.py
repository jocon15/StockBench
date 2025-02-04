from dataclasses import dataclass


@dataclass
class SingularSimulationChartPathBundle:
    """Encapsulates a set of analytic chart filepaths."""
    overview_chart_filepath: str
    buy_rules_chart_filepath: str
    sell_rules_chart_filepath: str
    account_value_bar_chart_filepath: str
    positions_duration_bar_chart_filepath: str
    positions_profit_loss_bar_chart_filepath: str
    positions_profit_loss_histogram_chart_filepath: str
