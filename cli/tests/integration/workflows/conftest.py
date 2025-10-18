"""Fixtures para testes E2E de workflows."""

from datetime import date, timedelta

import pytest


@pytest.fixture
def e2e_db_path(tmp_path):
    """Path para DB de E2E tests."""
    return tmp_path / "e2e_test.db"


@pytest.fixture
def complete_routine_setup(integration_session, sample_routine, sample_habits):
    """Setup completo: rotina + hábitos + instâncias geradas."""
    from src.timeblock.services.habit_instance_service import HabitInstanceService

    today = date.today()
    end_date = today + timedelta(days=7)

    instances = []
    for habit in sample_habits:
        habit_instances = HabitInstanceService.generate_instances(
            habit_id=habit.id, start_date=today, end_date=end_date
        )
        instances.extend(habit_instances)

    return {
        "routine": sample_routine,
        "habits": sample_habits,
        "instances": instances,
        "date_range": (today, end_date),
    }


@pytest.fixture
def mock_today(monkeypatch):
    """Mock date.today() para testes determinísticos."""
    from datetime import date

    test_date = date(2025, 10, 20)

    class MockDate(date):
        @classmethod
        def today(cls):
            return test_date

    monkeypatch.setattr("datetime.date", MockDate)
    return test_date
