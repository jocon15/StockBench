import logging
import os

from StockBench.controllers.function_tools.timestamp import datetime_timestamp
from StockBench.models.logging_handlers.file_log_handler import FileLogHandler


class LoggingController:

    USER_LOGGER_NAME = 'user_logger'
    DEV_LOGGER_NAME = 'dev_logger'

    LOGS_FOLDER = 'logs'
    DEV_FOLDER = 'dev'

    @staticmethod
    def enable_log_saving() -> None:
        """Enable user logging_handlers."""
        user_logger = logging.getLogger(LoggingController.USER_LOGGER_NAME)

        user_logger.setLevel(logging.INFO)
        user_logging_filepath = os.path.join(LoggingController.LOGS_FOLDER, f'RunLog_{datetime_timestamp()}')

        # make the directories if they don't already exist
        os.makedirs(os.path.dirname(user_logging_filepath), exist_ok=True)

        user_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')
        user_logging_handler = FileLogHandler(user_logging_filepath)
        user_logging_handler.setFormatter(user_logging_formatter)
        user_logger.addHandler(user_logging_handler)

    @staticmethod
    def enable_developer_logging(level: int = 2) -> None:
        """Enable developer logging handlers."""
        dev_logger = logging.getLogger(LoggingController.DEV_LOGGER_NAME)

        if level == 1:
            dev_logger.setLevel(logging.DEBUG)
            developer_logging_formatter = logging.Formatter('%(funcName)s:%(lineno)d|%(levelname)s|%(message)s')
        elif level == 3:
            dev_logger.setLevel(logging.WARNING)
            developer_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')
        elif level == 4:
            dev_logger.setLevel(logging.ERROR)
            developer_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')
        elif level == 5:
            dev_logger.setLevel(logging.CRITICAL)
            developer_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')
        else:
            dev_logger.setLevel(logging.INFO)
            developer_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')

        developer_logging_filepath = os.path.join(LoggingController.DEV_FOLDER, f'DevLog_{datetime_timestamp()}')

        # make the directories if they don't already exist
        os.makedirs(os.path.dirname(developer_logging_filepath), exist_ok=True)

        developer_logging_handler = FileLogHandler(developer_logging_filepath)
        developer_logging_handler.setFormatter(developer_logging_formatter)
        dev_logger.addHandler(developer_logging_handler)
