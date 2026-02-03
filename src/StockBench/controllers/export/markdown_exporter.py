import os
from datetime import datetime

from pandas import DataFrame

from StockBench.models.constants.simulation_results_constants import *


class MarkdownExporter:
    MARKDOWN_DIR = "markdown"

    @staticmethod
    def export_singular_simulation_to_md(simulation_results: dict) -> str:
        """Export a singular simulation to Markdown.

        Pasting the chart file HTML into the md file seems like a good idea, but the HTML file is too big (2MB).
        Because of how much data and wrapping code is in the file, the md file becomes un-loadable.
        """
        df = DataFrame()
        df["Metric"] = ["Start Date", "End Date", "Initial Account Value", "Trade-able Days", "Trades Made",
                        "Average Trade Duration", "Effectiveness", "Total PL", "Average PL", "Median PL",
                        "Standard PL Deviation", "Average PLPC", "Median PLPC", "Standard PLPC Deviation",
                        "Final Account Value"]
        df["Value"] = [MarkdownExporter._unix_to_date(simulation_results[SIMULATION_START_TIMESTAMP_KEY]),
                       MarkdownExporter._unix_to_date(simulation_results[SIMULATION_END_TIMESTAMP_KEY]),
                       f"$ {simulation_results[INITIAL_ACCOUNT_VALUE_KEY]}",
                       simulation_results[TRADE_ABLE_DAYS_KEY],
                       simulation_results[TRADES_MADE_KEY],
                       f"{simulation_results[AVERAGE_TRADE_DURATION_KEY]} days",
                       f"{simulation_results[EFFECTIVENESS_KEY]} %",
                       f"$ {simulation_results[TOTAL_PL_KEY]}",
                       f"$ {simulation_results[AVERAGE_PL_KEY]}",
                       f"$ {simulation_results[MEDIAN_PL_KEY]}",
                       f"$ {simulation_results[STANDARD_DEVIATION_PL_KEY]}",
                       f"{simulation_results[AVERAGE_PLPC_KEY]} %",
                       f"{simulation_results[MEDIAN_PLPC_KEY]} %",
                       f"{simulation_results[STANDARD_DEVIATION_PLPC_KEY]} %",
                       f"$ {simulation_results[FINAL_ACCOUNT_VALUE_KEY]}"]

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

        rel_filepath = os.path.join(MarkdownExporter.MARKDOWN_DIR,
                                    f"Singular_Results_{MarkdownExporter._datetime_filename()}.md")

        os.makedirs(os.path.dirname(rel_filepath), exist_ok=True)

        with open(rel_filepath, 'w') as file:
            file.writelines(MarkdownExporter._add_new_line_chars(lines))

        return rel_filepath

    @staticmethod
    def export_multi_simulation_to_md(simulation_results: dict) -> str:
        """Export a multi simulation to Markdown.

        Pasting the chart file HTML into the md file seems like a good idea, but the HTML file is too big (2MB).
        Because of how much data and wrapping code is in the file, the md file becomes un-loadable.
        """
        df = DataFrame()
        df["Metric"] = ["Start Date", "End Date", "Initial Account Value", "Trade-able Days", "Trades Made",
                        "Average Trade Duration", "Effectiveness", "Total PL", "Average PL", "Median PL",
                        "Standard PL Deviation", "Average PLPC", "Median PLPC", "Standard PLPC Deviation"]
        df["Value"] = [MarkdownExporter._unix_to_date(simulation_results[SIMULATION_START_TIMESTAMP_KEY]),
                       MarkdownExporter._unix_to_date(simulation_results[SIMULATION_END_TIMESTAMP_KEY]),
                       f"$ {simulation_results[INITIAL_ACCOUNT_VALUE_KEY]}",
                       simulation_results[TRADE_ABLE_DAYS_KEY],
                       simulation_results[TRADES_MADE_KEY],
                       f"{simulation_results[AVERAGE_TRADE_DURATION_KEY]} days",
                       f"{simulation_results[EFFECTIVENESS_KEY]} %",
                       f"$ {simulation_results[TOTAL_PL_KEY]}",
                       f"$ {simulation_results[AVERAGE_PL_KEY]}",
                       f"$ {simulation_results[MEDIAN_PL_KEY]}",
                       f"$ {simulation_results[STANDARD_DEVIATION_PL_KEY]}",
                       f"$ {simulation_results[AVERAGE_PLPC_KEY]}",
                       f"$ {simulation_results[MEDIAN_PLPC_KEY]}",
                       f"$ {simulation_results[STANDARD_DEVIATION_PLPC_KEY]}"]

        markdown_table = df.to_markdown(index=False)

        symbols_str = ", ".join(simulation_results[SYMBOLS_KEY])

        lines = [
            f"# Simulation Results",
            "#### Strategy",
            f"{simulation_results[STRATEGY_KEY]}",
            "#### Symbols",
            f"{symbols_str}",
            "#### Results",
            f"{markdown_table}",
            "#### Observations",
            "[Insert your observations here]",
            "#### Analysis",
            "[Insert your analysis here]",
        ]

        rel_filepath = os.path.join(MarkdownExporter.MARKDOWN_DIR,
                                    f"Multi_Results_{MarkdownExporter._datetime_filename()}.md")

        os.makedirs(os.path.dirname(rel_filepath), exist_ok=True)

        with open(rel_filepath, 'w') as file:
            file.writelines(MarkdownExporter._add_new_line_chars(lines))

        return rel_filepath

    @staticmethod
    def export_folder_simulation_to_md(simulation_results: dict) -> str:
        """Export a folder simulation to Markdown.

        Pasting the chart file HTML into the md file seems like a good idea, but the HTML file is too big (2MB).
        Because of how much data and wrapping code is in the file, the md file becomes un-loadable.
        """

        df = DataFrame()
        df["Metric"] = ["Start Date", "End Date", "Initial Account Value", "Trade-able Days", "Trades Made",
                        "Average Trade Duration", "Effectiveness", "Total PL", "Average PL", "Median PL",
                        "Standard PL Deviation", "Average PLPC", "Median PLPC", "Standard PLPC Deviation"]
        for strategy_results in simulation_results['results']:
            df[strategy_results[STRATEGY_KEY]] = [
                MarkdownExporter._unix_to_date(strategy_results[SIMULATION_START_TIMESTAMP_KEY]),
                MarkdownExporter._unix_to_date(strategy_results[SIMULATION_END_TIMESTAMP_KEY]),
                f"$ {strategy_results[INITIAL_ACCOUNT_VALUE_KEY]}",
                strategy_results[TRADE_ABLE_DAYS_KEY],
                strategy_results[TRADES_MADE_KEY],
                f"{strategy_results[AVERAGE_TRADE_DURATION_KEY]} days",
                f"{strategy_results[EFFECTIVENESS_KEY]} %",
                f"$ {strategy_results[TOTAL_PL_KEY]}",
                f"$ {strategy_results[AVERAGE_PL_KEY]}",
                f"$ {strategy_results[MEDIAN_PL_KEY]}",
                f"$ {strategy_results[STANDARD_DEVIATION_PL_KEY]}",
                f"$ {simulation_results[AVERAGE_PLPC_KEY]}",
                f"$ {simulation_results[MEDIAN_PLPC_KEY]}",
                f"$ {simulation_results[STANDARD_DEVIATION_PLPC_KEY]}"]

        markdown_table = df.to_markdown(index=False)

        symbols_str = ", ".join(simulation_results['results'][0][SYMBOLS_KEY])

        lines = [
            f"# Simulation Results",
            "#### Symbols",
            f"{symbols_str}",
            "#### Results",
            f"{markdown_table}",
            "#### Observations",
            "[Insert your observations here]",
            "#### Analysis",
            "[Insert your analysis here]",
        ]

        rel_filepath = os.path.join(MarkdownExporter.MARKDOWN_DIR,
                                    f"Folder_Results_{MarkdownExporter._datetime_filename()}.md")

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
