"""Unit tests for date_helpers module."""

from datetime import UTC, datetime

from src.timeblock.utils.date_helpers import (
    add_months,
    get_day_range,
    get_month_range,
    get_week_range,
)


class TestAddMonths:
    """Tests for add_months function."""

    def test_add_one_month(self):
        """Should add one month correctly."""
        base = datetime(2025, 1, 15, 10, 0, tzinfo=UTC)
        result = add_months(base, 1)
        assert result.month == 2
        assert result.year == 2025

    def test_add_negative_month(self):
        """Should subtract months correctly."""
        base = datetime(2025, 3, 15, 10, 0, tzinfo=UTC)
        result = add_months(base, -1)
        assert result.month == 2
        assert result.year == 2025

    def test_add_twelve_months(self):
        """Should handle year rollover."""
        base = datetime(2025, 1, 15, 10, 0, tzinfo=UTC)
        result = add_months(base, 12)
        assert result.month == 1
        assert result.year == 2026

    def test_add_zero_months(self):
        """Should return same date."""
        base = datetime(2025, 6, 15, 10, 0, tzinfo=UTC)
        result = add_months(base, 0)
        assert result == base

    def test_december_to_january(self):
        """Should handle December to January transition."""
        base = datetime(2025, 12, 15, 10, 0, tzinfo=UTC)
        result = add_months(base, 1)
        assert result.month == 1
        assert result.year == 2026

    def test_january_to_december(self):
        """Should handle January to December transition."""
        base = datetime(2025, 1, 15, 10, 0, tzinfo=UTC)
        result = add_months(base, -1)
        assert result.month == 12
        assert result.year == 2024


class TestGetWeekRange:
    """Tests for get_week_range function."""

    def test_current_week(self):
        """Should return current week range."""
        start, end = get_week_range(0)
        assert start.weekday() == 0  # Monday
        assert (end - start).days == 7
        assert start.hour == 0
        assert start.minute == 0

    def test_next_week(self):
        """Should return next week range."""
        current_start, _ = get_week_range(0)
        next_start, _ = get_week_range(1)
        assert (next_start - current_start).days == 7

    def test_previous_week(self):
        """Should return previous week range."""
        current_start, _ = get_week_range(0)
        prev_start, _ = get_week_range(-1)
        assert (current_start - prev_start).days == 7

    def test_week_starts_monday(self):
        """Should always start on Monday."""
        for offset in range(-5, 6):
            start, _ = get_week_range(offset)
            assert start.weekday() == 0

    def test_week_duration(self):
        """Should always span exactly 7 days."""
        for offset in range(-5, 6):
            start, end = get_week_range(offset)
            assert (end - start).days == 7


class TestGetMonthRange:
    """Tests for get_month_range function."""

    def test_current_month(self):
        """Should return current month range."""
        start, end = get_month_range(0)
        assert start.day == 1
        assert start.hour == 0
        assert end.day == 1

    def test_next_month(self):
        """Should return next month range."""
        current_start, _ = get_month_range(0)
        next_start, _ = get_month_range(1)

        # Next month should be 1 month later
        assert next_start > current_start
        assert next_start.day == 1

    def test_previous_month(self):
        """Should return previous month range."""
        current_start, _ = get_month_range(0)
        prev_start, _ = get_month_range(-1)

        assert prev_start < current_start
        assert prev_start.day == 1

    def test_month_starts_first_day(self):
        """Should always start on day 1."""
        for offset in range(-12, 13):
            start, _ = get_month_range(offset)
            assert start.day == 1

    def test_end_is_next_month_start(self):
        """End should be start of next month."""
        start, end = get_month_range(0)
        assert end.day == 1
        # End should be approximately 28-31 days after start
        assert 28 <= (end - start).days <= 31


class TestGetDayRange:
    """Tests for get_day_range function."""

    def test_today(self):
        """Should return today's range."""
        start, end = get_day_range(0)
        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0
        assert (end - start).days == 1

    def test_tomorrow(self):
        """Should return tomorrow's range."""
        today_start, _ = get_day_range(0)
        tomorrow_start, _ = get_day_range(1)
        assert (tomorrow_start - today_start).days == 1

    def test_yesterday(self):
        """Should return yesterday's range."""
        today_start, _ = get_day_range(0)
        yesterday_start, _ = get_day_range(-1)
        assert (today_start - yesterday_start).days == 1

    def test_day_duration(self):
        """Should always span exactly 1 day."""
        for offset in range(-10, 11):
            start, end = get_day_range(offset)
            assert (end - start).days == 1

    def test_day_starts_midnight(self):
        """Should always start at 00:00:00."""
        for offset in range(-10, 11):
            start, _ = get_day_range(offset)
            assert start.hour == 0
            assert start.minute == 0
            assert start.second == 0
