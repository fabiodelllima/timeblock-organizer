"""Date range filter construction for event list command."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from .date_helpers import get_month_range, get_week_range, get_day_range


class DateFilterBuilder:
    """Builds date range filters from CLI arguments."""

    def __init__(self, now: Optional[datetime] = None):
        """Initialize with current time (allows mocking in tests).

        Args:
            now: Reference datetime. If None, uses current UTC time.
        """
        self.now = now or datetime.now(timezone.utc)

    def build_from_args(
        self,
        weeks: Optional[int] = None,
        all_events: bool = False,
        limit: Optional[int] = None,
        month: Optional[str] = None,
        week: Optional[str] = None,
        day: Optional[str] = None,
    ) -> Tuple[Optional[datetime], Optional[datetime], Optional[int]]:
        """Build date filter from CLI arguments.

        Returns:
            Tuple of (start_date, end_date, limit)

        Priority order:
            1. limit (overrides everything)
            2. all_events (no date filter)
            3. month
            4. week
            5. day
            6. weeks (default)
        """
        # Priority 1: Limit takes precedence
        if limit is not None:
            return (None, None, limit)

        # Priority 2: All events
        if all_events:
            return (None, None, None)

        # Priority 3: Month filter
        if month is not None:
            return self._build_month_filter(month)

        # Priority 4: Week filter
        if week is not None:
            return self._build_week_filter(week)

        # Priority 5: Day filter
        if day is not None:
            return self._build_day_filter(day)

        # Priority 6: Default to weeks
        return self._build_weeks_filter(weeks or 2)

    def _build_month_filter(self, month: str) -> Tuple[datetime, datetime, None]:
        """Build filter for specific month.

        Args:
            month: Either absolute month (1-12) or relative offset (+/-N).
        """
        if month.startswith(("+", "-")):
            # Relative offset
            offset = int(month)
            start, end = get_month_range(offset)
        else:
            # Absolute month (1-12)
            target_month = int(month)
            current_month = self.now.month
            offset = target_month - current_month
            start, end = get_month_range(offset)

        return (start, end, None)

    def _build_week_filter(self, week: str) -> Tuple[datetime, datetime, None]:
        """Build filter for specific week."""
        offset = int(week)
        start, end = get_week_range(offset)
        return (start, end, None)

    def _build_day_filter(self, day: str) -> Tuple[datetime, datetime, None]:
        """Build filter for specific day."""
        offset = int(day)
        start, end = get_day_range(offset)
        return (start, end, None)

    def _build_weeks_filter(self, weeks: int) -> Tuple[datetime, datetime, None]:
        """Build filter for next N weeks."""
        start = self.now
        end = start + timedelta(weeks=weeks)
        return (start, end, None)
