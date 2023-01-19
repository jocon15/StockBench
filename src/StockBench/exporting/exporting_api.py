from datetime import datetime
import xlsxwriter


class ExportingAPI:
    def __init__(self):
        self.__workbook = xlsxwriter.Workbook(f'excel\\simulation_{self.__nonce()}')

    @staticmethod
    def __nonce():
        """Convert current date and time to string."""
        return datetime.now().strftime("%m_%d_%Y__%H_%M_%S")
