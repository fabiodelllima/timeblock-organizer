"""Integration tests for list command filters."""

import pytest
from typer.testing import CliRunner
from datetime import datetime, timezone, timedelta


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Isolate database for tests."""
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(tmp_path / "test.db"))
    import sys
    for mod in ["src.timeblock.database", "src.timeblock.commands.list", "src.timeblock.main"]:
        sys.modules.pop(mod, None)


@pytest.fixture
def sample_events(isolated_db):
    """Create sample events."""
    from src.timeblock.main import app
    runner = CliRunner()
    
    # Init database
    runner.invoke(app, ["init"])
    
    # Add events
    now = datetime.now(timezone.utc)
    runner.invoke(app, ["add", "Event Today", "-s", "09:00", "-e", "10:00"])
    
    return runner


def test_list_with_month_filter(sample_events):
    """Should filter by month."""
    from src.timeblock.main import app
    result = sample_events.invoke(app, ["list", "--month", "0"])
    assert result.exit_code == 0


def test_list_with_week_filter(sample_events):
    """Should filter by week."""
    from src.timeblock.main import app
    result = sample_events.invoke(app, ["list", "--week", "0"])
    assert result.exit_code == 0


def test_list_with_day_filter(sample_events):
    """Should filter by day."""
    from src.timeblock.main import app
    result = sample_events.invoke(app, ["list", "--day", "0"])
    assert result.exit_code == 0


def test_list_with_limit(sample_events):
    """Should limit results."""
    from src.timeblock.main import app
    result = sample_events.invoke(app, ["list", "--limit", "5"])
    assert result.exit_code == 0
    assert "Latest 5 Events" in result.output or "5" in result.output


def test_list_all_events(sample_events):
    """Should show all events."""
    from src.timeblock.main import app
    result = sample_events.invoke(app, ["list", "--all"])
    assert result.exit_code == 0
