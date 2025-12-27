import logging
import os

from StockBench.controllers.function_tools.timestamp import datetime_timestamp

log = logging.getLogger()


class LoggingController:
    LOGS_FOLDER = 'logs'
    DEV_FOLDER = 'dev'

    @staticmethod
    def enable_log_saving() -> None:
        """Enable user logging_handlers."""
        log.setLevel(logging.INFO)
        user_logging_filepath = os.path.join(LoggingController.LOGS_FOLDER, f'RunLog_{datetime_timestamp()}')

        # make the directories if they don't already exist
        os.makedirs(os.path.dirname(user_logging_filepath), exist_ok=True)

        user_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')
        user_handler = logging.FileHandler(user_logging_filepath)
        user_handler.setFormatter(user_logging_formatter)
        log.addHandler(user_handler)

    @staticmethod
    def enable_developer_logging(level: int = 2) -> None:
        """Enable developer logging handlers."""
        if level == 1:
            log.setLevel(logging.DEBUG)
            developer_logging_formatter = logging.Formatter('%(funcName)s:%(lineno)d|%(levelname)s|%(message)s')
        elif level == 3:
            log.setLevel(logging.WARNING)
            developer_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')
        elif level == 4:
            log.setLevel(logging.ERROR)
            developer_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')
        elif level == 5:
            log.setLevel(logging.CRITICAL)
            developer_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')
        else:
            log.setLevel(logging.INFO)
            developer_logging_formatter = logging.Formatter('%(levelname)s|%(message)s')

        developer_logging_filepath = os.path.join(LoggingController.DEV_FOLDER, f'DevLog_{datetime_timestamp()}')

        # make the directories if they don't already exist
        os.makedirs(os.path.dirname(developer_logging_filepath), exist_ok=True)

        developer_handler = logging.FileHandler(developer_logging_filepath)
        developer_handler.setFormatter(developer_logging_formatter)
        log.addHandler(developer_handler)
