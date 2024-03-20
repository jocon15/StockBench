import sys
import traceback
from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot


class WorkerSignals(QObject):
    """Singles for the worker to use."""
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    """Worker thread"""
    def __init__(self, function_to_execute, *args, **kwargs):
        """
        Args:
            function_to_execute: A reference to the function the qt_worker will be executing.
            *args: Any arguments needed to run the function defined by function_to_execute.
            **kwargs: Any keyword arguments needed to run the function defined by function_to_execute.
        """
        super(Worker, self).__init__()
        self.function_to_execute = function_to_execute
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.function_to_execute(*self.args, **self.kwargs)
        except:  # noqa
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]  # noqa
            self.signals.error.emit((exctype, value, traceback.format_exc()))  # noqa
        else:
            self.signals.result.emit(result)  # noqa # Return the result of the processing
        finally:
            self.signals.finished.emit()  # noqa # Done