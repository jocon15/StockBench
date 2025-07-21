import os
from datetime import datetime

from pandas import DataFrame

from StockBench.constants import *


class MarkdownExporter:
    @staticmethod
    def export_singular_simulation_to_md(simulation_results: dict) -> str:
        """Export a singular simulation to markdown.

        Pasting the chart file html into the md file seems like a good idea, but the html file is too big (2MB)
        Because of how much data and wrapping code is in the file, the md file becomes un-loadable in any application.
        """
        df = DataFrame()
        df["Metric"] = ["Start Date", "End Date", "Initial Account Balance", "Trade-able Days", "Trades Made",
                        "Average Trade Duration", "Effectiveness", "Total Profit/Loss", "Average Profit/Loss",
                        "Median Profit/Loss", "Standard Profit/Loss Deviation", "Account Value"]
        df["Value"] = [MarkdownExporter._unix_to_date(simulation_results[SIMULATION_START_TIMESTAMP_KEY]),
                       MarkdownExporter._unix_to_date(simulation_results[SIMULATION_END_TIMESTAMP_KEY]),
                       f"$ {simulation_results[INITIAL_ACCOUNT_VALUE_KEY]}",
                       simulation_results[TRADE_ABLE_DAYS_KEY],
                       simulation_results[TRADES_MADE_KEY],
                       f"{simulation_results[AVERAGE_TRADE_DURATION_KEY]} days",
                       f"{simulation_results[EFFECTIVENESS_KEY]} %",
                       f"$ {simulation_results[TOTAL_PROFIT_LOSS_KEY]}",
                       f"$ {simulation_results[AVERAGE_PROFIT_LOSS_KEY]}",
                       f"$ {simulation_results[MEDIAN_PROFIT_LOSS_KEY]}",
                       f"$ {simulation_results[STANDARD_PROFIT_LOSS_DEVIATION_KEY]}",
                       f"$ {simulation_results[ACCOUNT_VALUE_KEY]}"]

        markdown_table = df.to_markdown(index=False)

        lines = [
            f"# {simulation_results[SYMBOL_KEY]} Simulation Results",
            "#### Strategy",
            f"{simulation_results[STRATEGY_KEY]}",
            "#### Results",
            f"{markdown_table}",
            "#### Observations",
            "[Insert your observations here]",
            "#### Analysis",
            "[Insert your analysis here]",
        ]

        rel_filepath = os.path.join("markdown", f"Singular_Results_{MarkdownExporter._datetime_filename()}.md")

        os.makedirs(os.path.dirname(rel_filepath), exist_ok=True)

        with open(rel_filepath, 'w') as file:
            file.writelines(MarkdownExporter._add_new_line_chars(lines))

        return rel_filepath

    @staticmethod
    def _add_new_line_chars(lines: list) -> list:
        return [f"{line} \r\n" for line in lines]

    @staticmethod
    def _datetime_filename(timestamp_format="%m_%d_%Y__%H_%M_%S") -> str:
        """Create a datetime filename using the current timestamp."""
        return datetime.now().strftime(timestamp_format)

    @staticmethod
    def _unix_to_date(timestamp: int) -> str:
        """Convert a unix timestamp to a date."""
        return datetime.fromtimestamp(timestamp).strftime("%m/%d/%Y")
