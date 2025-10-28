import logging
from logging import Handler


class ProgressMessageHandler(Handler):
    """Custom log handler for progress messages.

    This handler is used to route log messages to a progress observer. The progress observer maintains a queue of
    progress messages to be output to the gui, which is running on a different thread. Simulator uses a non-generic
    custom logger to log progress based messages intended for viewing in the gui. That custom logger uses this custom
    handler to get the log messages into the progress observer queue."""
    def __init__(self, progress_observer):
        self.progress_observer = progress_observer
        logging.Handler.__init__(self=self)

    def emit(self, record: logging.LogRecord) -> None:
        """Add the log message to the progress observer."""
        self.progress_observer.add_log_record(record)
