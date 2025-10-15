from xlsxwriter.worksheet import Worksheet
from StockBench.controllers.export.base.excel_exporter import ExcelExporter
from StockBench.controllers.function_tools.timestamp import datetime_timestamp
from StockBench.constants import *


class FolderResultsExporter(ExcelExporter):
    WORKSHEET_NAME = 'Results'

    def export(self, results: list, folder_path: str, file_name_prefix: str) -> str:
        timestamp = datetime_timestamp()

        workbook, filepath = self._open_workbook(folder_path, file_name_prefix, timestamp)
        worksheet = workbook.add_worksheet(self.WORKSHEET_NAME)

        self.__write_column_headers(worksheet)
        self.__write_results(results, worksheet)

        self._close_workbook(workbook)

        return filepath

    def __write_column_headers(self, worksheet: Worksheet):
        worksheet.write_string(self.DATA_COLUMN_HEADER_ROW, 0, 'Strategy')
        worksheet.write_string(self.DATA_COLUMN_HEADER_ROW, 1, 'Trades Made')
        worksheet.write_string(self.DATA_COLUMN_HEADER_ROW, 2, 'Effectiveness')
        worksheet.write_string(self.DATA_COLUMN_HEADER_ROW, 3, 'Total P/L')
        worksheet.write_string(self.DATA_COLUMN_HEADER_ROW, 4, 'Average P/L')
        worksheet.write_string(self.DATA_COLUMN_HEADER_ROW, 5, 'Median P/L')
        worksheet.write_string(self.DATA_COLUMN_HEADER_ROW, 6, 'Stddev(P) P/L')

    def __write_results(self, results: list, worksheet: Worksheet):
        if len(results) == 0:
            raise ValueError('Results is empty!')
        col = self.DATA_COLUMN_HEADER_COL
        row = self.DATA_COLUMN_HEADER_ROW + 1
        for result in results:
            self._write_to_cell(worksheet, row, col, result[STRATEGY_KEY])
            self._write_to_cell(worksheet, row, col+1, result[TRADES_MADE_KEY])
            self._write_to_cell(worksheet, row, col+2, result[EFFECTIVENESS_KEY])
            self._write_to_cell(worksheet, row, col+3, result[TOTAL_PROFIT_LOSS_KEY])
            self._write_to_cell(worksheet, row, col+4, result[AVERAGE_PROFIT_LOSS_KEY])
            self._write_to_cell(worksheet, row, col+5, result[MEDIAN_PROFIT_LOSS_KEY])
            self._write_to_cell(worksheet, row, col+6, result[STANDARD_PROFIT_LOSS_DEVIATION_KEY])
            row += 1
