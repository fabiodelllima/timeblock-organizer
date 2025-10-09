"""Date manipulation utilities for time range calculations."""

from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta


def add_months(base_date: datetime, months_offset: int) -> datetime:
    """Add or subtract months from a datetime.

    Args:
        base_date: Starting datetime.
        months_offset: Number of months to add (positive) or subtract (negative).

    Returns:
        New datetime with months added/subtracted.

    Examples:
        >>> from datetime import datetime
        >>> date = datetime(2025, 1, 15)
        >>> add_months(date, 2)  # March 15, 2025
        >>> add_months(date, -1)  # December 15, 2024
    """
    return base_date + relativedelta(months=months_offset)


def get_month_range(months_offset: int = 0) -> tuple[datetime, datetime]:
    """Get start and end dates for a month with relative offset.

    Args:
        months_offset: Number of months from current month.
                      0 = this month, +1 = next month, -1 = last month.

    Returns:
        Tuple of (start_of_month, end_of_month) as timezone-aware datetimes.

    Examples:
        >>> # This month
        >>> start, end = get_month_range(0)
        >>> # Next month
        >>> start, end = get_month_range(+1)
    """
    now = datetime.now(timezone.utc)
    target_month = add_months(now, months_offset)

    # Start: first day of month at 00:00:00
    start_of_month = target_month.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    # End: first day of next month at 00:00:00
    end_of_month = add_months(start_of_month, 1)

    return (start_of_month, end_of_month)


def get_week_range(weeks_offset: int = 0) -> tuple[datetime, datetime]:
    """Get start and end dates for a week with relative offset.

    Week is defined as Monday 00:00:00 to Sunday 23:59:59.

    Args:
        weeks_offset: Number of weeks from current week.
                     0 = this week, +1 = next week, -1 = last week.

    Returns:
        Tuple of (start_of_week, end_of_week) as timezone-aware datetimes.

    Examples:
        >>> # This week
        >>> start, end = get_week_range(0)
        >>> # Last week
        >>> start, end = get_week_range(-1)
    """
    now = datetime.now(timezone.utc)

    # Calculate start of current week (Monday)
    days_since_monday = now.weekday()
    start_of_current_week = now - timedelta(days=days_since_monday)
    start_of_current_week = start_of_current_week.replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # Apply offset
    start_of_target_week = start_of_current_week + timedelta(weeks=weeks_offset)

    # End is 7 days later
    end_of_target_week = start_of_target_week + timedelta(days=7)

    return (start_of_target_week, end_of_target_week)


def get_day_range(days_offset: int = 0) -> tuple[datetime, datetime]:
    """Get start and end times for a day with relative offset.

    Args:
        days_offset: Number of days from today.
                    0 = today, +1 = tomorrow, -1 = yesterday.

    Returns:
        Tuple of (start_of_day, end_of_day) as timezone-aware datetimes.

    Examples:
        >>> # Today
        >>> start, end = get_day_range(0)
        >>> # Tomorrow
        >>> start, end = get_day_range(+1)
    """
    now = datetime.now(timezone.utc)
    target_day = now + timedelta(days=days_offset)

    # Start: 00:00:00 of target day
    start_of_day = target_day.replace(hour=0, minute=0, second=0, microsecond=0)

    # End: 00:00:00 of next day
    end_of_day = start_of_day + timedelta(days=1)

    return (start_of_day, end_of_day)
