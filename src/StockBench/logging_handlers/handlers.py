import logging
from logging import Handler


class ProgressMessageHandler(Handler):
    """Custom log handler that is used to write log messages to the progress observer's message queue."""
    def __init__(self, progress_observer):
        self.progress_observer = progress_observer
        logging.Handler.__init__(self=self)

    def emit(self, record) -> None:
        self.progress_observer.add_message(record)
