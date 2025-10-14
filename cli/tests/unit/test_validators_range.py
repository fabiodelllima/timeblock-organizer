"""Tests for validate_time_range function."""

import pytest
from datetime import datetime
from datetime import timezone as tz
from src.timeblock.utils.validators import validate_time_range


class TestValidateTimeRange:
    """Tests for validate_time_range()."""

    def test_valid_range(self):
        """Should accept valid time range."""
        time = datetime.now(tz.utc).replace(second=0, microsecond=0)
        start = time
        end = time.replace(hour=(time.hour + 2) % 24)
        
        # Should not raise
        result = validate_time_range(start, end)
        # Returns end (possibly adjusted)
        assert result is not None

    def test_valid_range_small_gap(self):
        """Should accept 1 minute gap."""
        time = datetime.now(tz.utc).replace(second=0, microsecond=0)
        start = time
        end = time.replace(minute=(time.minute + 1) % 60)
        
        # Should not raise for >= 1 minute
        validate_time_range(start, end)

    def test_same_time_rejects_24h(self):
        """Should REJECT same time (24h duration)."""
        time = datetime.now(tz.utc).replace(second=0, microsecond=0)
        
        # Same time = 24h after adjustment = INVALID
        with pytest.raises(ValueError, match="cannot be 24 hours or more"):
            validate_time_range(time, time)

    def test_end_before_start_valid_crossing_midnight(self):
        """Should handle midnight crossing for valid duration."""
        time = datetime.now(tz.utc).replace(hour=23, minute=0, second=0, microsecond=0)
        start = time
        end = time.replace(hour=2)  # 02:00 (crosses midnight)
        
        # Should adjust end to next day
        result = validate_time_range(start, end)
        
        # Result should be next day
        assert result.hour == 2
        assert result.day == end.day + 1

    def test_end_one_second_before_valid(self):
        """Should handle end 1 second before start as midnight crossing."""
        time = datetime.now(tz.utc).replace(second=0, microsecond=0)
        start = time
        end = time.replace(second=59, hour=(time.hour - 1) % 24)
        
        # Should not raise (crosses midnight)
        validate_time_range(start, end)
