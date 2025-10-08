"""Input validation utilities."""

from datetime import datetime


def parse_time(time_str: str, base_date: datetime) -> datetime:
    """Parse time string (HH:MM) and combine with base date.

    Args:
        time_str: Time in HH:MM format (e.g., "14:30").
        base_date: Base datetime to combine with.

    Returns:
        Parsed datetime with time from time_str and date from base_date.

    Raises:
        ValueError: If time format is invalid or values out of range.

    Examples:
        >>> from datetime import datetime, timezone
        >>> now = datetime.now(timezone.utc)
        >>> parse_time("14:30", now)
        datetime.datetime(2025, 10, 7, 14, 30, 0, 0, tzinfo=datetime.timezone.utc)
    """
    try:
        hour, minute = map(int, time_str.split(":"))

        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError(f"Invalid time: {time_str}")

        return base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    except (ValueError, AttributeError) as e:
        raise ValueError(
            f"Invalid time format: {time_str}. Use HH:MM (e.g., 14:30)"
        ) from e


def is_valid_hex_color(color: str) -> bool:
    """Validate hex color format.

    Args:
        color: Color string to validate.

    Returns:
        True if valid hex color format (#RRGGBB), False otherwise.

    Examples:
        >>> is_valid_hex_color("#3498db")
        True
        >>> is_valid_hex_color("#FF5733")
        True
        >>> is_valid_hex_color("3498db")
        False
        >>> is_valid_hex_color("#ZZZ")
        False
    """
    if not color.startswith("#"):
        return False

    if len(color) != 7:
        return False

    try:
        int(color[1:], 16)
        return True
    except ValueError:
        return False


def validate_time_range(start: datetime, end: datetime) -> None:
    """Validate that start time is before end time.

    Args:
        start: Start datetime.
        end: End datetime.

    Raises:
        ValueError: If end is not after start.

    Examples:
        >>> from datetime import datetime, timezone, timedelta
        >>> now = datetime.now(timezone.utc)
        >>> later = now + timedelta(hours=1)
        >>> validate_time_range(now, later)  # OK, no exception
        >>> validate_time_range(later, now)  # Raises ValueError
        Traceback (most recent call last):
        ...
        ValueError: End time must be after start time
    """
    if end <= start:
        raise ValueError("End time must be after start time")
