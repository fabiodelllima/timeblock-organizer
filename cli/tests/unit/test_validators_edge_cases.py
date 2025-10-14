"""Tests for validator edge cases."""
import pytest
from datetime import datetime, timedelta
from datetime import timezone as tz
from src.timeblock.utils.validators import validate_time_range


def test_validate_duration_less_than_one_minute():
    """Should raise error for events shorter than 1 minute."""
    now = datetime.now(tz.utc).replace(second=0, microsecond=0)
    start = now
    end = start + timedelta(seconds=30)
    
    with pytest.raises(ValueError, match="at least 1 minute long"):
        validate_time_range(start, end)


def test_validate_exactly_one_minute():
    """Should accept event of exactly 1 minute."""
    now = datetime.now(tz.utc).replace(second=0, microsecond=0)
    start = now
    end = start + timedelta(minutes=1)
    
    # Should not raise
    adjusted = validate_time_range(start, end)
    assert adjusted == end


def test_validate_24_hours_exact():
    """Should reject event of exactly 24 hours."""
    now = datetime.now(tz.utc).replace(second=0, microsecond=0)
    start = now
    end = start  # Same time = 24h after adjustment
    
    with pytest.raises(ValueError, match="cannot be 24 hours or more"):
        validate_time_range(start, end)


def test_validate_more_than_24_hours():
    """Should reject event longer than 24 hours."""
    now = datetime.now(tz.utc).replace(second=0, microsecond=0)
    start = now
    end = start + timedelta(hours=25)
    
    with pytest.raises(ValueError, match="cannot be 24 hours or more"):
        validate_time_range(start, end)


def test_validate_23_hours_59_minutes():
    """Should accept maximum valid duration (< 24h)."""
    now = datetime.now(tz.utc).replace(second=0, microsecond=0)
    start = now
    end = start + timedelta(hours=23, minutes=59)
    
    # Should not raise
    adjusted = validate_time_range(start, end)
    assert adjusted == end


def test_midnight_crossing_detection():
    """Should detect and adjust midnight crossing."""
    # Same day: 23:00 and 02:00
    base = datetime.now(tz.utc).replace(hour=23, minute=0, second=0, microsecond=0)
    start = base
    end = base.replace(hour=2, minute=0)  # 02:00 same day
    
    # Should detect end < start and add 1 day
    adjusted = validate_time_range(start, end)
    
    # Adjusted should be next day at 02:00
    expected = end + timedelta(days=1)
    assert adjusted == expected
    
    # Duration should be 3 hours
    duration = (adjusted - start).total_seconds()
    assert duration == 3 * 3600


def test_normal_case_no_crossing():
    """Should not adjust when end > start (normal case)."""
    now = datetime.now(tz.utc).replace(second=0, microsecond=0)
    start = now
    end = now + timedelta(hours=2)
    
    adjusted = validate_time_range(start, end)
    
    # Should return end unchanged
    assert adjusted == end
