from datetime import datetime


def datetime_timestamp(nonce_format="%m_%d_%Y__%H_%M_%S"):
    """Convert current date and time to string.

    Args:
        nonce_format (str): The desired format of the nonce value.
    """
    return datetime.now().strftime(nonce_format)
