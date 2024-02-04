import os


class Display:
    """Base class for a display."""

    NO_SAVE = 0
    TEMP_SAVE = 1
    UNIQUE_SAVE = 2

    @staticmethod
    def save_chart(figure, filename) -> str:
        """Saves a chart to a file.

        Args:
            figure(str): The html string of the chart.
            filename(str): The name of the file to save as.

        Return:
            (str): The filepath of the saved chart.
        """
        chart_filepath = os.path.join('figures', filename)
        # make the directories if they don't already exist
        os.makedirs(os.path.dirname(chart_filepath), exist_ok=True)

        with open(chart_filepath, 'w', encoding="utf-8") as file:
            file.write(figure)

        return chart_filepath
