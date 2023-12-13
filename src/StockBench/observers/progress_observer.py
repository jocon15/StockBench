import threading


class ProgressObserver:
    """"""
    def __init__(self):
        self._current_progress = 0.0
        self._max_progress = 100.0
        self._completed = False
        self.lock = threading.Lock()

    def update_progress(self, advance: float):
        """"""
        # acquire lock to be thread-safe
        with self.lock:
            if advance + self._current_progress > self._max_progress:
                # If the advance will exceed the max progress, set progress to full progress.
                # This will prevent the progress from going out of bounds in a gui if the advance does not evently
                # divide the max progress (100)
                self._completed = True
                self._current_progress = self._max_progress
            else:
                self._current_progress += advance

    def get_progress(self) -> float:
        """"""
        # acquire lock to be thread-safe
        with self.lock:
            return self._current_progress

    def is_completed(self) -> bool:
        # acquire lock to be thread-safe
        with self.lock:
            return self._completed
