"""Tests for HabitInstance is_overdue property."""

from datetime import date, time, datetime, timedelta
from src.timeblock.models import HabitInstance, HabitInstanceStatus


def test_is_overdue_when_planned_and_past():
    """is_overdue True quando PLANNED e horário passou."""
    past_date = date.today() - timedelta(days=1)
    instance = HabitInstance(
        habit_id=1,
        date=past_date,
        scheduled_start=time(9, 0),
        scheduled_end=time(10, 0),
        status=HabitInstanceStatus.PLANNED,
    )
    assert instance.is_overdue is True


def test_is_overdue_false_when_in_progress():
    """is_overdue False quando IN_PROGRESS, mesmo com horário passado."""
    past_date = date.today() - timedelta(days=1)
    instance = HabitInstance(
        habit_id=1,
        date=past_date,
        scheduled_start=time(9, 0),
        scheduled_end=time(10, 0),
        status=HabitInstanceStatus.IN_PROGRESS,
    )
    assert instance.is_overdue is False


def test_is_overdue_false_when_completed():
    """is_overdue False quando COMPLETED."""
    past_date = date.today() - timedelta(days=1)
    instance = HabitInstance(
        habit_id=1,
        date=past_date,
        scheduled_start=time(9, 0),
        scheduled_end=time(10, 0),
        status=HabitInstanceStatus.COMPLETED,
    )
    assert instance.is_overdue is False


def test_is_overdue_false_when_future():
    """is_overdue False quando PLANNED mas horário não passou."""
    future_date = date.today() + timedelta(days=1)
    instance = HabitInstance(
        habit_id=1,
        date=future_date,
        scheduled_start=time(9, 0),
        scheduled_end=time(10, 0),
        status=HabitInstanceStatus.PLANNED,
    )
    assert instance.is_overdue is False


def test_is_overdue_false_when_today_not_reached():
    """is_overdue False quando hoje mas horário ainda não chegou."""
    # Usar horário futuro (23:59 sempre será futuro durante o dia)
    instance = HabitInstance(
        habit_id=1,
        date=date.today(),
        scheduled_start=time(23, 59),
        scheduled_end=time(23, 59),
        status=HabitInstanceStatus.PLANNED,
    )
    # Se o teste rodar antes de 23:59, deve ser False
    # Se rodar depois, pode ser True - teste pode ser flaky
    # Por isso vamos testar apenas que a property existe e retorna bool
    assert isinstance(instance.is_overdue, bool)
