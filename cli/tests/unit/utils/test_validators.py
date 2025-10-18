"""Consolidated tests for validators module."""

from datetime import UTC, datetime, timedelta

import pytest

from src.timeblock.utils.validators import (
    is_valid_hex_color,
    parse_time,
    validate_time_range,
)

# ============================================================================
# ParseTime Tests
# ============================================================================


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


# ============================================================================
# HexColor Tests
# ============================================================================


class TestIsValidHexColor:
    """Tests for is_valid_hex_color function."""

    def test_valid_lowercase(self):
        """Should accept valid lowercase hex color."""
        assert is_valid_hex_color("#ff5733") is True

    def test_valid_uppercase(self):
        """Should accept valid uppercase hex color."""
        assert is_valid_hex_color("#FF5733") is True

    def test_valid_mixed_case(self):
        """Should accept valid mixed case hex color."""
        assert is_valid_hex_color("#Ff5733") is True

    def test_valid_all_zeros(self):
        """Should accept #000000."""
        assert is_valid_hex_color("#000000") is True

    def test_valid_all_fs(self):
        """Should accept #FFFFFF."""
        assert is_valid_hex_color("#FFFFFF") is True

    def test_invalid_no_hash(self):
        """Should reject color without #."""
        assert is_valid_hex_color("FF5733") is False

    def test_invalid_too_short(self):
        """Should reject color with less than 6 hex digits."""
        assert is_valid_hex_color("#FF57") is False

    def test_invalid_too_long(self):
        """Should reject color with more than 6 hex digits."""
        assert is_valid_hex_color("#FF573344") is False

    def test_invalid_non_hex_chars(self):
        """Should reject color with non-hex characters."""
        assert is_valid_hex_color("#GG5733") is False

    def test_invalid_special_chars(self):
        """Should reject color with special characters."""
        assert is_valid_hex_color("#FF57@3") is False

    def test_empty_string(self):
        """Should reject empty string."""
        assert is_valid_hex_color("") is False

    def test_only_hash(self):
        """Should reject only hash symbol."""
        assert is_valid_hex_color("#") is False


# ============================================================================
# TimeRange Tests
# ============================================================================


class TestValidateTimeRange:
    """Tests for validate_time_range()."""

    def test_valid_range(self):
        """Should accept valid time range."""
        time = datetime.now(UTC).replace(second=0, microsecond=0)
        start = time
        end = time.replace(hour=(time.hour + 2) % 24)
        result = validate_time_range(start, end)
        assert result is not None

    def test_valid_range_small_gap(self):
        """Should accept 1 minute gap."""
        time = datetime.now(UTC).replace(second=0, microsecond=0)
        start = time
        end = time.replace(minute=(time.minute + 1) % 60)
        validate_time_range(start, end)

    def test_same_time_rejects_24h(self):
        """Should REJECT same time (24h duration)."""
        time = datetime.now(UTC).replace(second=0, microsecond=0)
        with pytest.raises(ValueError, match="cannot be 24 hours or more"):
            validate_time_range(time, time)

    def test_end_before_start_valid_crossing_midnight(self):
        """Should handle midnight crossing for valid duration."""
        time = datetime.now(UTC).replace(hour=23, minute=0, second=0, microsecond=0)
        start = time
        end = time.replace(hour=2)
        result = validate_time_range(start, end)
        assert result.hour == 2
        assert result.day == end.day + 1

    def test_end_one_second_before_valid(self):
        """Should handle end 1 second before start as midnight crossing."""
        time = datetime.now(UTC).replace(second=0, microsecond=0)
        start = time
        end = time.replace(second=59, hour=(time.hour - 1) % 24)
        validate_time_range(start, end)

    def test_validate_duration_less_than_one_minute(self):
        """Should raise error for events shorter than 1 minute."""
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        start = now
        end = start + timedelta(seconds=30)
        with pytest.raises(ValueError, match="at least 1 minute long"):
            validate_time_range(start, end)

    def test_validate_exactly_one_minute(self):
        """Should accept event of exactly 1 minute."""
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        start = now
        end = start + timedelta(minutes=1)
        adjusted = validate_time_range(start, end)
        assert adjusted == end

    def test_validate_24_hours_exact(self):
        """Should reject event of exactly 24 hours."""
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        start = now
        end = start
        with pytest.raises(ValueError, match="cannot be 24 hours or more"):
            validate_time_range(start, end)

    def test_validate_more_than_24_hours(self):
        """Should reject event longer than 24 hours."""
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        start = now
        end = start + timedelta(hours=25)
        with pytest.raises(ValueError, match="cannot be 24 hours or more"):
            validate_time_range(start, end)

    def test_validate_23_hours_59_minutes(self):
        """Should accept maximum valid duration (< 24h)."""
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        start = now
        end = start + timedelta(hours=23, minutes=59)
        adjusted = validate_time_range(start, end)
        assert adjusted == end

    def test_midnight_crossing_detection(self):
        """Should detect and adjust midnight crossing."""
        base = datetime.now(UTC).replace(hour=23, minute=0, second=0, microsecond=0)
        start = base
        end = base.replace(hour=2, minute=0)
        adjusted = validate_time_range(start, end)
        expected = end + timedelta(days=1)
        assert adjusted == expected
        duration = (adjusted - start).total_seconds()
        assert duration == 3 * 3600

    def test_normal_case_no_crossing(self):
        """Should not adjust when end > start (normal case)."""
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        start = now
        end = now + timedelta(hours=2)
        adjusted = validate_time_range(start, end)
        assert adjusted == end
