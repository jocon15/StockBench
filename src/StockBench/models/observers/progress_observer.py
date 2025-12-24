import queue
import threading
from queue import Queue
from logging import LogRecord


class ProgressObserver:
    """Progress observer is used via dependency injection to keep track of task progress
    in tasks where the task might be un-trackable using other methods due to abstraction
    layers. It is primarily used for keeping track of a task's progress from a GUI
    component for displaying task progress in as a progress bar.

    Progress observer is thread-safe.
    """
    def __init__(self):
        # locks
        self.__progress_lock = threading.Lock()

        # defaults
        self.__message_queue = Queue()
        self.__current_progress = 0.0
        self.__max_progress = 100.0
        self.__analytics_completed = False
        self.__charting_completed = False

    def update_progress(self, advance: float):
        """Update the progress of the task."""
        advance = round(advance, 3)
        with self.__progress_lock:
            if advance + self.__current_progress >= self.__max_progress:
                # If the advance will exceed the max progress, set progress to full progress.
                # This will prevent the progress from going out of bounds in a gui if the advance does not evently
                # divide the max progress (100)
                self.__current_progress = self.__max_progress
            else:
                self.__current_progress += advance

    def get_progress(self) -> float:
        """Get the progress of the task."""
        with self.__progress_lock:
            return self.__current_progress

    def add_log_record(self, record: LogRecord):
        # reminder that queue is threadsafe by default (don't need locks)
        self.__message_queue.put(record)

    def get_messages(self) -> list:
        """Gets a list of messages from the queue.

        WARNING:
            This function inherently removes queue messages once they are read from the queue.
            Calling clients must be aware that any queue messages read by calling this function will be destroyed.
            After calling, the queue will be empty until more messages are added to the queue.
        """
        # reminder that queue is threadsafe by default (don't need locks)
        messages = []
        try:
            item = self.__message_queue.get_nowait()
            messages.append(item)
            # print(f"Processing {item}")  # helpful for debugging queue
            self.__message_queue.task_done()  # Mark the task as done
        except queue.Empty:
            # print("Queue is currently empty")  # helpful for debugging queue
            pass
        return messages

    def set_analytics_complete(self):
        """Manually list the analytics as complete."""
        with self.__progress_lock:
            print("Analytics is complete")
            self.__analytics_completed = True

    def set_charting_complete(self):
        """Manually list the charting as complete."""
        with self.__progress_lock:
            print("Charting is complete")
            self.__charting_completed = True

    def is_simulation_completed(self) -> bool:
        """See if the simulation is complete."""
        with self.__progress_lock:
            return self.__analytics_completed and self.__charting_completed

    def is_analytics_completed(self) -> bool:
        """See if the analytics are complete."""
        with self.__progress_lock:
            return self.__analytics_completed

    def is_charting_completed(self) -> bool:
        """See if the charting is complete."""
        with self.__progress_lock:
            return self.__charting_completed
