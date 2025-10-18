"""Unit tests for event_date_filters module."""

from datetime import UTC, datetime

import pytest

from src.timeblock.utils.event_date_filters import DateFilterBuilder


class TestDateFilterBuilderInit:
    """Tests for DateFilterBuilder initialization."""

    def test_init_with_now(self):
        """Should use provided now value."""
        fixed_now = datetime(2025, 6, 15, 12, 0, tzinfo=UTC)
        builder = DateFilterBuilder(now=fixed_now)
        assert builder.now == fixed_now

    def test_init_without_now(self):
        """Should use current UTC time."""
        builder = DateFilterBuilder()
        assert builder.now is not None
        assert builder.now.tzinfo is not None


class TestBuildFromArgsPriority:
    """Tests for argument priority in build_from_args."""

    @pytest.fixture
    def builder(self):
        """Fixed time builder for consistent tests."""
        fixed_now = datetime(2025, 6, 15, 12, 0, tzinfo=UTC)
        return DateFilterBuilder(now=fixed_now)

    def test_limit_overrides_all(self, builder):
        """Limit should override all other filters."""
        start, end, limit = builder.build_from_args(
            limit=10, all_events=True, month="1", week="0", day="0", weeks=2
        )
        assert start is None
        assert end is None
        assert limit == 10

    def test_all_events_overrides_filters(self, builder):
        """all_events should override date filters."""
        start, end, limit = builder.build_from_args(
            all_events=True, month="1", week="0", day="0", weeks=2
        )
        assert start is None
        assert end is None
        assert limit is None

    def test_month_overrides_week_day_weeks(self, builder):
        """month should take precedence over week/day/weeks."""
        start, end, limit = builder.build_from_args(month="1", week="0", day="0", weeks=2)
        assert start is not None
        assert end is not None
        assert limit is None

    def test_week_overrides_day_weeks(self, builder):
        """week should take precedence over day/weeks."""
        start, end, limit = builder.build_from_args(week="0", day="0", weeks=2)
        assert start is not None
        assert start.weekday() == 0
        assert limit is None

    def test_day_overrides_weeks(self, builder):
        """day should take precedence over weeks."""
        start, end, limit = builder.build_from_args(day="0", weeks=2)
        assert start is not None
        assert start.hour == 0
        assert (end - start).days == 1

    def test_weeks_default(self, builder):
        """Should default to weeks filter."""
        start, end, limit = builder.build_from_args(weeks=3)
        assert start is not None
        assert end is not None
        assert (end - start).days == 21

    def test_no_args_defaults_to_two_weeks(self, builder):
        """No arguments should default to 2 weeks."""
        start, end, limit = builder.build_from_args()
        assert start is not None
        assert end is not None
        assert (end - start).days == 14


class TestMonthFilter:
    """Tests for _build_month_filter."""

    @pytest.fixture
    def builder(self):
        """Fixed time builder."""
        fixed_now = datetime(2025, 6, 15, 12, 0, tzinfo=UTC)
        return DateFilterBuilder(now=fixed_now)

    def test_relative_month_positive(self, builder):
        """Should handle +1 (next month)."""
        start, end, limit = builder.build_from_args(month="+1")
        assert start.day == 1
        assert start.hour == 0
        assert end.day == 1
        assert limit is None
        assert 28 <= (end - start).days <= 31

    def test_relative_month_negative(self, builder):
        """Should handle -1 (last month)."""
        start, end, limit = builder.build_from_args(month="-1")
        assert start.day == 1
        assert end.day == 1
        assert 28 <= (end - start).days <= 31

    def test_absolute_month(self, builder):
        """Should handle absolute month."""
        start, end, limit = builder.build_from_args(month="12")
        assert start.day == 1
        assert end.day == 1
        assert 28 <= (end - start).days <= 31


class TestWeekFilter:
    """Tests for _build_week_filter."""

    @pytest.fixture
    def builder(self):
        """Fixed time builder."""
        fixed_now = datetime(2025, 6, 15, 12, 0, tzinfo=UTC)
        return DateFilterBuilder(now=fixed_now)

    def test_current_week(self, builder):
        """Should return current week (Monday-Sunday)."""
        start, end, limit = builder.build_from_args(week="0")
        assert start.weekday() == 0
        assert (end - start).days == 7
        assert limit is None

    def test_next_week(self, builder):
        """Should return next week."""
        current_start, _, _ = builder.build_from_args(week="0")
        next_start, _, _ = builder.build_from_args(week="+1")
        assert next_start.weekday() == 0
        assert (next_start - current_start).days == 7

    def test_last_week(self, builder):
        """Should return last week."""
        current_start, _, _ = builder.build_from_args(week="0")
        last_start, _, _ = builder.build_from_args(week="-1")
        assert last_start.weekday() == 0
        assert (current_start - last_start).days == 7


class TestDayFilter:
    """Tests for _build_day_filter."""

    @pytest.fixture
    def builder(self):
        """Fixed time builder."""
        fixed_now = datetime(2025, 6, 15, 12, 0, tzinfo=UTC)
        return DateFilterBuilder(now=fixed_now)

    def test_today(self, builder):
        """Should return today's range."""
        start, end, limit = builder.build_from_args(day="0")
        assert start.hour == 0
        assert start.minute == 0
        assert (end - start).days == 1
        assert limit is None

    def test_tomorrow(self, builder):
        """Should return tomorrow's range."""
        today_start, _, _ = builder.build_from_args(day="0")
        tomorrow_start, _, _ = builder.build_from_args(day="+1")
        assert (tomorrow_start - today_start).days == 1

    def test_yesterday(self, builder):
        """Should return yesterday's range."""
        today_start, _, _ = builder.build_from_args(day="0")
        yesterday_start, _, _ = builder.build_from_args(day="-1")
        assert (today_start - yesterday_start).days == 1


class TestWeeksFilter:
    """Tests for _build_weeks_filter."""

    @pytest.fixture
    def builder(self):
        """Fixed time builder."""
        fixed_now = datetime(2025, 6, 15, 12, 0, tzinfo=UTC)
        return DateFilterBuilder(now=fixed_now)

    def test_one_week(self, builder):
        """Should return 1 week range."""
        start, end, limit = builder.build_from_args(weeks=1)
        assert (end - start).days == 7
        assert limit is None

    def test_four_weeks(self, builder):
        """Should return 4 weeks range."""
        start, end, limit = builder.build_from_args(weeks=4)
        assert (end - start).days == 28

    def test_starts_from_now(self, builder):
        """Should start from current time."""
        start, end, limit = builder.build_from_args(weeks=2)
        assert start == builder.now
