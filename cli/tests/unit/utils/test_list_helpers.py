"""Tests for list command helper functions."""

from src.timeblock.commands.list import _describe_filter


def test_describe_filter_with_month():
    """Should return month description."""
    desc = _describe_filter(all_events=False, limit=None, month="+1", week=None, day=None)
    assert desc == " for month +1"


def test_describe_filter_with_week():
    """Should return week description."""
    desc = _describe_filter(all_events=False, limit=None, month=None, week="0", day=None)
    assert desc == " for week 0"


def test_describe_filter_with_day():
    """Should return day description."""
    desc = _describe_filter(all_events=False, limit=None, month=None, week=None, day="+1")
    assert desc == " for day +1"


def test_describe_filter_default():
    """Should return default 2 weeks description."""
    desc = _describe_filter(all_events=False, limit=None, month=None, week=None, day=None)
    assert desc == " for next 2 weeks"


def test_describe_filter_with_limit():
    """Should return limit description."""
    desc = _describe_filter(all_events=False, limit=10, month=None, week=None, day=None)
    assert desc == " (showing latest 10)"


def test_describe_filter_with_all_events():
    """Should return empty string for all events."""
    desc = _describe_filter(all_events=True, limit=None, month=None, week=None, day=None)
    assert desc == ""
