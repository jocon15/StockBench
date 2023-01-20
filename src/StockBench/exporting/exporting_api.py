import os
import math
import logging
import xlsxwriter
from datetime import datetime

log = logging.getLogger()


class ExportingAPI:
    """This class defines an exporting object.

    This exporting object is used as an API for the simulator to export data to excel.

    The user may want to see the physical data used during the simulation. (This can also help us debug)
    The exporting feature allows us to export the entire simulation (simulation window) data to an Excel file.
    The rendered Excel file looks exactly like the Pandas DataFrame."""
    def __init__(self):
        self.__df = None

        self.__NONCE = self.__nonce()
        report_filepath = f'excel\\simulation_{self.__NONCE}.xlsx'
        # make the directories if they don't already exist
        os.makedirs(os.path.dirname(report_filepath), exist_ok=True)
        self.__workbook = xlsxwriter.Workbook(report_filepath)
        self.__data_worksheet = self.__workbook.add_worksheet('Data')

        # Data worksheet offsets
        self.__DATA_COLUMN_HEADER_ROW = 3
        self.__DATA_COLUMN_HEADER_COL = 0

    def __del__(self):
        self.__workbook.close()

    def load_data(self, data):
        """Load the simulation data."""
        self.__df = data

    def export(self):
        """Export the data to an Excel file."""
        self.__add_titles()
        self.__write_df()
        # write anything else here

    def __add_titles(self):
        """Add titles to the worksheet."""
        self.__data_worksheet.write_string(0, 0, f'Simulation data for simulation_{self.__NONCE}')

    def __write_df(self):
        """Write the DateFrame data to the worksheet."""
        if self.__df.empty:
            raise Exception('Data needs to be uploaded first')
        col = self.__DATA_COLUMN_HEADER_COL
        for (column_name, column_data) in self.__df.iteritems():
            # FIXME: print the column name here
            self.__data_worksheet.write_string(self.__DATA_COLUMN_HEADER_ROW, col, column_name)
            row = self.__DATA_COLUMN_HEADER_ROW + 1
            for element in column_data:
                if element:
                    # print(f'{element} {type(element)}')
                    if type(element) == float:
                        if math.isnan(element):
                            # print nothing for nan
                            self.__data_worksheet.write_string(row, col, '')
                        else:
                            self.__data_worksheet.write(row, col, element)
                    elif type(element) == str:
                        self.__data_worksheet.write_string(row, col, element)
                    else:
                        self.__data_worksheet.write(row, col, element)
                row += 1
            col += 1

    @staticmethod
    def __nonce():
        """Convert current date and time to string."""
        return datetime.now().strftime("%m_%d_%Y__%H_%M_%S")
