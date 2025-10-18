"""Tests for workflow fixtures."""

import pytest


@pytest.mark.skip(reason="Requer migration de tag_id em Habit - Opção 3: Features Pendentes")
def test_complete_routine_setup(complete_routine_setup):
    """Test complete routine workflow setup."""
    routine, habits, instances = complete_routine_setup

    assert routine.id is not None
    assert len(habits) == 2
    assert len(instances) > 0

    for habit in habits:
        assert habit.routine_id == routine.id

    for instance in instances:
        assert instance.habit_id in [h.id for h in habits]
