from logging import LogRecord, FileHandler


class FileLogHandler(FileHandler):
    """Encapsulates a log handler for file logging.

    The simulation log messages may contain characters that cannot be written to files (check mark symbol). This handler
    will remove the troublesome symbols.
    """
    def __init__(self, filepath: str):
        super().__init__(filepath)

    def emit(self, record: LogRecord):
        """Remove troublesome characters from the log message."""
        stripped = (c for c in record.msg if 0 < ord(c) < 127)
        record.msg = ''.join(stripped)

        super().emit(record)
