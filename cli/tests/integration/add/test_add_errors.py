"""Tests for error handling in add command."""

import pytest
from typer.testing import CliRunner

from src.timeblock.main import app


@pytest.fixture
def runner():
    """Create CLI runner."""
    return CliRunner()


class TestAddErrors:
    """Test error cases for add command."""

    def test_add_invalid_time_format(self, isolated_db, runner):
        """Should reject invalid time format."""
        result = runner.invoke(
            app,
            ["add", "Meeting", "-s", "25:00", "-e", "10:00"],
        )
        assert result.exit_code == 1
        assert "Hour must be between 0 and 23" in result.output

    def test_add_start_after_end_valid_crossing_midnight(self, isolated_db, runner):
        """Start after end treated as crossing midnight (valid)."""
        result = runner.invoke(
            app,
            ["add", "Night Shift", "-s", "15:00", "-e", "14:00"],
        )
        assert result.exit_code == 0
        assert "crosses midnight" in result.output.lower()

    def test_add_invalid_hex_color_format(self, isolated_db, runner):
        """Should reject color without # prefix."""
        result = runner.invoke(
            app,
            ["add", "Meeting", "-s", "09:00", "-e", "10:00", "-c", "3498db"],
        )
        assert result.exit_code == 1
        assert "Invalid color format" in result.output

    def test_add_invalid_hex_color_length(self, isolated_db, runner):
        """Should reject color with wrong length."""
        result = runner.invoke(
            app,
            ["add", "Meeting", "-s", "09:00", "-e", "10:00", "-c", "#123"],
        )
        assert result.exit_code == 1
        assert "Invalid color format" in result.output
