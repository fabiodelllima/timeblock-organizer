"""Tests for list command helper functions."""

from src.timeblock.commands.list import _describe_filter


def test_describe_filter_with_month():
    """Should return month description (line 90)."""
    desc = _describe_filter(weeks=2, all_events=False, limit=None, month="+1", week=None, day=None)
    assert desc == " for month +1"


def test_describe_filter_with_week():
    """Should return week description (line 92)."""
    desc = _describe_filter(weeks=2, all_events=False, limit=None, month=None, week="0", day=None)
    assert desc == " for week 0"


def test_describe_filter_with_day():
    """Should return day description (line 94)."""
    desc = _describe_filter(weeks=2, all_events=False, limit=None, month=None, week=None, day="+1")
    assert desc == " for day +1"


def test_describe_filter_with_weeks():
    """Should return weeks description (line 96)."""
    desc = _describe_filter(weeks=4, all_events=False, limit=None, month=None, week=None, day=None)
    assert desc == " for next 4 weeks"


def test_describe_filter_with_limit():
    """Should return limit description (line 88)."""
    desc = _describe_filter(weeks=2, all_events=False, limit=10, month=None, week=None, day=None)
    assert desc == " (showing latest 10)"


def test_describe_filter_with_all_events():
    """Should return empty string for all events (line 90)."""
    desc = _describe_filter(weeks=2, all_events=True, limit=None, month=None, week=None, day=None)
    assert desc == ""
