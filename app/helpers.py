from datetime import datetime, timezone


def utc_now() -> datetime:
    """
    Returns the current UTC time.
    """
    return datetime.now(timezone.utc)
