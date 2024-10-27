from datetime import datetime


def datetime_timestamp(timestamp_format="%m_%d_%Y__%H_%M_%S"):
    """Convert current date and time to string.

    Args:
        timestamp_format: The desired format of the nonce value.
    """
    return datetime.now().strftime(timestamp_format)
