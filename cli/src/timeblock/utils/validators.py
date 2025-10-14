"""Input validation utilities."""

from datetime import datetime, timezone, timedelta
import re


def parse_time(time_str: str) -> datetime:
    """Parse time string to datetime with current date.
    
    Supports two formats:
    - HH:MM (e.g., "09:30", "14:00", "00:45")
    - HHh or HHhMM (e.g., "9h", "14h30", "0h", "0h45")
    
    Args:
        time_str: Time string in one of the supported formats
        
    Returns:
        datetime object with today's date and specified time (UTC)
        
    Raises:
        ValueError: If format is invalid or time values are out of range
        
    Examples:
        >>> parse_time("09:30")  # Traditional format
        >>> parse_time("9h30")   # Brazilian format
        >>> parse_time("14h")    # Hour only (minutes default to 00)
        >>> parse_time("0h45")   # After midnight
    """
    if not time_str or not isinstance(time_str, str):
        raise ValueError("Time string cannot be empty")
    
    time_str = time_str.strip()
    hour = None
    minute = None
    
    # Try format: HHh or HHhMM (e.g., "14h", "9h30", "0h45")
    h_pattern = r'^(\d{1,2})h(\d{1,2})?$'
    h_match = re.match(h_pattern, time_str)
    
    if h_match:
        hour = int(h_match.group(1))
        minute = int(h_match.group(2)) if h_match.group(2) else 0
    
    # Try format: HH:MM (e.g., "09:30", "14:00")
    elif ":" in time_str:
        parts = time_str.split(":")
        if len(parts) != 2:
            raise ValueError("Time must be in HH:MM or HHh or HHhMM format")
        
        try:
            hour = int(parts[0])
            minute = int(parts[1])
        except ValueError as e:
            raise ValueError("Time must contain only numbers") from e
    
    else:
        raise ValueError("Time must be in HH:MM or HHh or HHhMM format")
    
    # Validate ranges
    if not (0 <= hour <= 23):
        raise ValueError("Hour must be between 0 and 23")
    if not (0 <= minute <= 59):
        raise ValueError("Minute must be between 0 and 59")
    
    # Create datetime with current date
    now = datetime.now(timezone.utc)
    return now.replace(hour=hour, minute=minute, second=0, microsecond=0)


def is_valid_hex_color(color: str) -> bool:
    """Validate hexadecimal color code.
    
    Args:
        color: Color code (e.g., "#FF5733")
        
    Returns:
        True if valid hex color, False otherwise
    """
    if not color:
        return False
    
    pattern = r'^#[0-9A-Fa-f]{6}$'
    return bool(re.match(pattern, color))


def validate_time_range(start: datetime, end: datetime) -> datetime:
    """Validate and adjust time range for midnight crossing.
    
    Business Rules:
    1. If end <= start, assumes event crosses midnight (next day)
    2. Minimum duration: 1 minute
    3. Maximum duration: < 24 hours (time blocking is for specific tasks)
    
    Args:
        start: Start datetime (with date + time)
        end: End datetime (with date + time)
        
    Returns:
        Adjusted end datetime (may be +1 day if crossing midnight)
        
    Raises:
        ValueError: If duration is invalid
        
    Examples:
        >>> # Same day event
        >>> start = datetime(2025, 10, 14, 9, 0)
        >>> end = datetime(2025, 10, 14, 10, 30)
        >>> validate_time_range(start, end)  # Returns end unchanged
        
        >>> # Crosses midnight
        >>> start = datetime(2025, 10, 14, 23, 0)
        >>> end = datetime(2025, 10, 14, 2, 0)  # 02:00 same day
        >>> validate_time_range(start, end)
        >>> # Returns: datetime(2025, 10, 15, 2, 0)  # Next day!
    """
    # Detect midnight crossing: if end <= start, must be next day
    adjusted_end = end
    if end <= start:
        adjusted_end = end + timedelta(days=1)
    
    # Calculate duration in seconds
    duration = (adjusted_end - start).total_seconds()
    
    # Minimum duration: 1 minute
    if duration < 60:
        raise ValueError("Event must be at least 1 minute long")
    
    # Maximum duration: < 24 hours
    if duration >= 86400:
        raise ValueError(
            "Event duration cannot be 24 hours or more. "
            "Time blocking is designed for specific activities, not entire days."
        )
    
    return adjusted_end
