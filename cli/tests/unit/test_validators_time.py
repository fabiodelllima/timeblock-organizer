"""Tests for time parsing validation."""

import pytest
from datetime import datetime, timezone

from src.timeblock.utils.validators import parse_time


class TestParseTime:
    """Tests for parse_time function."""

    @pytest.fixture
    def base_date(self):
        """Base date for parsing tests."""
        return datetime(2025, 10, 7, tzinfo=timezone.utc)

    def test_parse_valid_time(self, base_date):
        """Should parse valid HH:MM format."""
        result = parse_time("14:30", base_date)
        assert result.hour == 14
        assert result.minute == 30
        assert result.tzinfo == timezone.utc

    def test_parse_midnight(self, base_date):
        """Should parse midnight correctly."""
        result = parse_time("00:00", base_date)
        assert result.hour == 0
        assert result.minute == 0

    def test_parse_end_of_day(self, base_date):
        """Should parse 23:59 correctly."""
        result = parse_time("23:59", base_date)
        assert result.hour == 23
        assert result.minute == 59

    def test_parse_with_leading_zeros(self, base_date):
        """Should handle leading zeros."""
        result = parse_time("09:05", base_date)
        assert result.hour == 9
        assert result.minute == 5

    def test_invalid_format_no_colon(self, base_date):
        """Should raise ValueError for missing colon."""
        with pytest.raises(ValueError, match="Invalid time format"):
            parse_time("1430", base_date)

    def test_invalid_format_letters(self, base_date):
        """Should raise ValueError for non-numeric input."""
        with pytest.raises(ValueError):
            parse_time("14:3a", base_date)

    def test_invalid_hour_too_high(self, base_date):
        """Should raise ValueError for hour > 23."""
        with pytest.raises(ValueError, match="Invalid time"):
            parse_time("25:30", base_date)

    def test_invalid_hour_negative(self, base_date):
        """Should raise ValueError for negative hour."""
        with pytest.raises(ValueError):
            parse_time("-1:30", base_date)

    def test_invalid_minute_too_high(self, base_date):
        """Should raise ValueError for minute > 59."""
        with pytest.raises(ValueError, match="Invalid time"):
            parse_time("14:75", base_date)

    def test_invalid_minute_negative(self, base_date):
        """Should raise ValueError for negative minute."""
        with pytest.raises(ValueError):
            parse_time("14:-5", base_date)

    def test_empty_string(self, base_date):
        """Should raise ValueError for empty string."""
        with pytest.raises(ValueError):
            parse_time("", base_date)
