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
    """Validate time range, handling midnight crossing.
    If end <= start, assumes event crosses midnight and adds 1 day to end.
    Returns adjusted end datetime.
    """
    # If end is before or equal to start, assume crossing midnight
    if end <= start:
        # This will be handled by the caller (add command)
        # Just validate that it's a reasonable duration (e.g., < 24 hours)
        duration = (end.replace(day=end.day + 1) - start).total_seconds()
        if duration > 86400:  # 24 hours
            raise ValueError("Event duration cannot exceed 24 hours")
        # Don't raise error - crossing midnight is valid
        return
    # Normal case: end > start
    if (end - start).total_seconds() < 60:
        raise ValueError("Event must be at least 1 minute long")
