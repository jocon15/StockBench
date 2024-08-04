import os

from typing import Tuple
from xlsxwriter.worksheet import Worksheet
from xlsxwriter.workbook import Workbook
import math
from abc import ABC


class ExcelExporter(ABC):
    DEFAULT_EXCEL_FOLDER = 'excel'
    DATA_COLUMN_HEADER_ROW = 3
    DATA_COLUMN_HEADER_COL = 0

    def _open_workbook(self, folder_path: str, file_name_prefix: str, timestamp: str) -> Tuple[Workbook, str]:
        filename = f'Simulation_{file_name_prefix}_{timestamp}.xlsx'

        if folder_path:
            export_filepath = os.path.join(folder_path, filename)
        else:
            export_filepath = os.path.join(self.DEFAULT_EXCEL_FOLDER, filename)
        # make the directories if they don't already exist
        os.makedirs(os.path.dirname(export_filepath), exist_ok=True)

        return Workbook(export_filepath), export_filepath

    @staticmethod
    def _close_workbook(workbook: Workbook):
        # if the workbook is still open, close it
        if workbook:
            workbook.close()

    @staticmethod
    def _write_to_cell(worksheet: Worksheet, row: int, col: int, value: any):
        if type(value) is float:
            if math.isnan(value):
                # print nothing for nan elements
                worksheet.write_string(row, col, '')
            else:
                worksheet.write(row, col, value)
        elif type(value) is str:
            worksheet.write_string(row, col, value)
        else:
            worksheet.write(row, col, value)
