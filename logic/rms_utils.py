from datetime import datetime, timezone


def convert_timestamp_to_datetime(timestamp: float) -> datetime:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
