"""Parse date shortcuts like 'today', 'this-week', etc."""
from datetime import date, timedelta
from typing import Tuple


def parse_date_shortcut(shortcut: str) -> date | Tuple[date, date] | None:
    """Parse date shortcuts.
    
    Returns:
        - date for single days
        - tuple (start, end) for ranges
        - None if not a recognized shortcut
    """
    today = date.today()
    
    # Single days
    if shortcut == "today":
        return today
    elif shortcut == "tomorrow":
        return today + timedelta(days=1)
    elif shortcut == "yesterday":
        return today - timedelta(days=1)
    
    # Weeks (return tuple)
    elif shortcut == "this-week":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return (start, end)
    elif shortcut == "next-week":
        start = today + timedelta(days=(7 - today.weekday()))
        end = start + timedelta(days=6)
        return (start, end)
    elif shortcut == "last-week":
        start = today - timedelta(days=(today.weekday() + 7))
        end = start + timedelta(days=6)
        return (start, end)
    
    # Months
    elif shortcut == "this-month":
        start = today.replace(day=1)
        next_month = (start + timedelta(days=32)).replace(day=1)
        end = next_month - timedelta(days=1)
        return (start, end)
    elif shortcut == "next-month":
        next_m = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        end = (next_m + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        return (next_m, end)
    
    return None
