import logging
from functools import wraps
from time import perf_counter

log = logging.getLogger()


def performance_timer(original_fxn):
    """Decorator for timing functions."""

    @wraps(original_fxn)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = original_fxn(*args, **kwargs)
        end = perf_counter()
        elapsed = end - start
        log.debug(f'Function: {original_fxn.__name__} took {elapsed} seconds')
        return result

    return wrapper
