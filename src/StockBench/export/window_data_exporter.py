from pandas import DataFrame
from xlsxwriter.worksheet import Worksheet
from StockBench.export.base.excel_exporter import ExcelExporter
from StockBench.function_tools.nonce import datetime_timestamp


class WindowDataExporter(ExcelExporter):
    """This class defines an export object.

    This export object is used as an API for the simulator to export data to excel.

    The user may want to see the physical data used during the simulation. (This can also help us debug)
    The export feature allows us to export the entire simulation (simulation window) data to an Excel file.
    The rendered Excel file looks exactly like the Pandas DataFrame."""
    WORKSHEET_NAME = 'Data'

    def export(self, df: DataFrame, symbol: str) -> str:
        """Export the data to an Excel file."""
        timestamp = datetime_timestamp()

        workbook, filepath = self._open_workbook('', symbol, timestamp)
        worksheet = workbook.add_worksheet(self.WORKSHEET_NAME)

        self.__add_titles(worksheet, symbol, timestamp)
        self.__write_df(df, worksheet)

        self._close_workbook(workbook)

        return filepath

    def __write_df(self, df: DataFrame, worksheet: Worksheet):
        """Write the DateFrame data to the worksheet."""
        if df.empty:
            raise ValueError('DataFrame is empty!')
        col = self.DATA_COLUMN_HEADER_COL
        for (column_name, column_data) in df.items():
            worksheet.write_string(self.DATA_COLUMN_HEADER_ROW, col, column_name)
            row = self.DATA_COLUMN_HEADER_ROW + 1
            for element in column_data:
                if element:
                    self._write_to_cell(worksheet, row, col, element)
                row += 1
            col += 1

    @staticmethod
    def __add_titles(worksheet: Worksheet, symbol: str, timestamp: str):
        """Add titles to the worksheet."""
        worksheet.write_string(0, 0, f'Simulation data for: {symbol}')
        worksheet.write_string(1, 0, f'simulation timestamp: {timestamp}')
