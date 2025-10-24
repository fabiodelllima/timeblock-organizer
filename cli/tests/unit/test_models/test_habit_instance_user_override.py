"""Tests for HabitInstance user_override field."""

from src.timeblock.models import HabitInstance


def test_user_override_default_false():
    """user_override deve ser False por padrão."""
    instance = HabitInstance(
        habit_id=1,
        date="2025-10-22",
        scheduled_start="09:00",
        scheduled_end="10:00",
    )
    assert instance.user_override is False


def test_user_override_can_be_set_true():
    """user_override deve aceitar True."""
    instance = HabitInstance(
        habit_id=1,
        date="2025-10-22",
        scheduled_start="09:00",
        scheduled_end="10:00",
        user_override=True,
    )
    assert instance.user_override is True
