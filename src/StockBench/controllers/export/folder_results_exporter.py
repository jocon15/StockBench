from xlsxwriter.worksheet import Worksheet
from StockBench.controllers.export.base.excel_exporter import ExcelExporter
from StockBench.controllers.function_tools.timestamp import datetime_timestamp
from StockBench.models.constants.simulation_results_constants import *


class FolderResultsExporter(ExcelExporter):
    WORKSHEET_NAME = 'Results'

    HEADERS = ['Strategy', 'Trades Made', 'Effectiveness (%)', 'Total PL ($)', 'Average PL ($)', 'Median PL ($)',
               'Stddev PL ($)', 'Average PLPC (%)', 'Median PLPC (%)', 'Stddev PLPC (%)']

    RESULTS_KEYS = [STRATEGY_KEY, TRADES_MADE_KEY, EFFECTIVENESS_KEY, TOTAL_PL_KEY, AVERAGE_PL_KEY, MEDIAN_PL_KEY,
                    STANDARD_DEVIATION_PL_KEY, AVERAGE_PLPC_KEY, MEDIAN_PLPC_KEY, STANDARD_DEVIATION_PLPC_KEY]

    def export(self, results: list, folder_path: str, file_name_prefix: str) -> str:
        timestamp = datetime_timestamp()

        workbook, filepath = self._open_workbook(folder_path, file_name_prefix, timestamp)
        worksheet = workbook.add_worksheet(self.WORKSHEET_NAME)

        self.__write_column_headers(worksheet)
        self.__write_results(results, worksheet)

        self._close_workbook(workbook)

        return filepath

    def __write_column_headers(self, worksheet: Worksheet):
        for i, header in enumerate(self.HEADERS):
            worksheet.write_string(self.DATA_COLUMN_HEADER_ROW, i, header)

    def __write_results(self, results: list, worksheet: Worksheet):
        if len(results) == 0:
            raise ValueError('Results is empty!')
        row = self.DATA_COLUMN_HEADER_ROW + 1

        for result in results:
            for col, result_key in enumerate(self.RESULTS_KEYS):
                self._write_to_cell(worksheet, row, col, result[result_key])
            row += 1
