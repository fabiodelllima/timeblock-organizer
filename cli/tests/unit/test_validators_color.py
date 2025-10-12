"""Tests for color validation."""

from src.timeblock.utils.validators import is_valid_hex_color


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
