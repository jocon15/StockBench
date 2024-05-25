import threading
from queue import Queue


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
        self.__completed = False

    def update_progress(self, advance: float):
        """Update the progress of the task.

        Args:
            advance (float): Amount to increase the progress by.
        """
        # acquire lock to be thread-safe
        with self.__progress_lock:
            if advance + self.__current_progress >= self.__max_progress:
                # If the advance will exceed the max progress, set progress to full progress.
                # This will prevent the progress from going out of bounds in a gui if the advance does not evently
                # divide the max progress (100)
                self.__completed = True
                self.__current_progress = self.__max_progress
            else:
                self.__current_progress += advance

    def get_progress(self) -> float:
        """Get the progress of the task."""
        # acquire lock to be thread-safe
        with self.__progress_lock:
            return self.__current_progress

    def add_message(self, message):
        # reminder that queue is threadsafe
        self.__message_queue.put(message)

    def get_messages(self) -> list:
        # reminder that queue is threadsafe
        messages = []
        if self.__message_queue.qsize() != 0:
            for _ in range(self.__message_queue.qsize()):
                messages.append(self.__message_queue.get())

            # release the queue lock
            self.__message_queue.task_done()
        return messages

    def is_completed(self) -> bool:
        """See if the task is complete."""
        # acquire lock to be thread-safe
        with self.__progress_lock:
            return self.__completed
