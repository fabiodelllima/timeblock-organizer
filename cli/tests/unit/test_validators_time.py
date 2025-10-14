"""Tests for parse_time function."""

import pytest
from datetime import datetime
from datetime import timezone as tz
from src.timeblock.utils.validators import parse_time


class TestParseTime:
    """Tests for parse_time()."""

    def test_parse_valid_time(self):
        """Should parse valid HH:MM format."""
        result = parse_time("14:30")
        assert result.hour == 14
        assert result.minute == 30

    def test_parse_midnight(self):
        """Should parse 00:00."""
        result = parse_time("00:00")
        assert result.hour == 0
        assert result.minute == 0

    def test_parse_end_of_day(self):
        """Should parse 23:59."""
        result = parse_time("23:59")
        assert result.hour == 23
        assert result.minute == 59

    def test_parse_with_leading_zeros(self):
        """Should parse times with leading zeros."""
        result = parse_time("09:05")
        assert result.hour == 9
        assert result.minute == 5

    # New format tests: HHh and HHhMM
    def test_parse_hour_only_format(self):
        """Should parse HHh format (e.g., '20h')."""
        result = parse_time("20h")
        assert result.hour == 20
        assert result.minute == 0

    def test_parse_hour_minute_format(self):
        """Should parse HHhMM format (e.g., '21h30')."""
        result = parse_time("21h30")
        assert result.hour == 21
        assert result.minute == 30

    def test_parse_single_digit_hour(self):
        """Should parse single digit hour (e.g., '9h')."""
        result = parse_time("9h")
        assert result.hour == 9
        assert result.minute == 0

    def test_parse_midnight_h_format(self):
        """Should parse midnight as '0h'."""
        result = parse_time("0h")
        assert result.hour == 0
        assert result.minute == 0

    def test_parse_midnight_with_minutes(self):
        """Should parse '0h30'."""
        result = parse_time("0h30")
        assert result.hour == 0
        assert result.minute == 30

    def test_parse_leading_zero_h_format(self):
        """Should parse '00h45'."""
        result = parse_time("00h45")
        assert result.hour == 0
        assert result.minute == 45

    def test_parse_single_digit_minutes(self):
        """Should parse single digit minutes (e.g., '9h05')."""
        result = parse_time("9h05")
        assert result.hour == 9
        assert result.minute == 5

    # Invalid format tests
    def test_invalid_format_no_separator(self):
        """Should reject format without colon or 'h'."""
        with pytest.raises(ValueError, match="HH:MM or HHh or HHhMM"):
            parse_time("1430")

    def test_invalid_format_letters(self):
        """Should reject non-numeric characters."""
        with pytest.raises(ValueError, match="must contain only numbers"):
            parse_time("14:3a")

    def test_invalid_hour_too_high(self):
        """Should reject hour > 23."""
        with pytest.raises(ValueError, match="Hour must be between 0 and 23"):
            parse_time("25:30")

    def test_invalid_hour_negative(self):
        """Should reject negative hour."""
        with pytest.raises(ValueError, match="Hour must be between 0 and 23"):
            parse_time("-1:30")

    def test_invalid_minute_too_high(self):
        """Should reject minute > 59."""
        with pytest.raises(ValueError, match="Minute must be between 0 and 59"):
            parse_time("14:75")

    def test_invalid_minute_negative(self):
        """Should reject negative minute."""
        with pytest.raises(ValueError, match="Minute must be between 0 and 59"):
            parse_time("14:-5")

    def test_empty_string(self):
        """Should reject empty string."""
        with pytest.raises(ValueError, match="cannot be empty"):
            parse_time("")

    def test_invalid_h_format_too_many_parts(self):
        """Should reject malformed h format."""
        with pytest.raises(ValueError, match="HH:MM or HHh or HHhMM"):
            parse_time("14h30h")

    def test_invalid_hour_in_h_format(self):
        """Should reject invalid hour in h format."""
        with pytest.raises(ValueError, match="Hour must be between 0 and 23"):
            parse_time("25h")

    def test_invalid_minute_in_h_format(self):
        """Should reject invalid minute in h format."""
        with pytest.raises(ValueError, match="Minute must be between 0 and 59"):
            parse_time("14h75")
