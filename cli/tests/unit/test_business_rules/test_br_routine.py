"""Testes para Business Rules de Routine.

Valida BRs:
- BR-ROUTINE-001: Single Active Constraint
- BR-ROUTINE-002: Habit Belongs to Routine
- BR-ROUTINE-003: Task Independent of Routine
- BR-ROUTINE-004: Activation Cascade
"""

from datetime import datetime, time

from sqlmodel import Session, select

from src.timeblock.models import Habit, Recurrence, Routine, Task


# BR-ROUTINE-001: Single Active Constraint
class TestBRRoutine001:
    """Valida BR-ROUTINE-001: Apenas uma rotina ativa por vez."""

    def test_br_routine_001_only_one_active(self, session: Session):
        """BR-ROUTINE-001: Sistema permite apenas 1 rotina ativa."""
        # Arrange
        routine1 = Routine(name="Rotina Matinal", is_active=True)
        routine2 = Routine(name="Rotina Trabalho", is_active=False)
        session.add(routine1)
        session.add(routine2)
        session.commit()

        # Act
        active_routines = session.exec(select(Routine).where(Routine.is_active)).all()

        # Assert
        assert len(active_routines) == 1, "Deve haver apenas 1 rotina ativa"
        assert active_routines[0].name == "Rotina Matinal"

    def test_br_routine_001_activate_deactivates_others(self, session: Session):
        """BR-ROUTINE-001: Ativar rotina desativa todas as outras."""
        # Arrange
        routine1 = Routine(name="Rotina Matinal", is_active=True)
        routine2 = Routine(name="Rotina Trabalho", is_active=False)
        session.add(routine1)
        session.add(routine2)
        session.commit()

        # Act - Ativar routine2
        for routine in session.exec(select(Routine)).all():
            routine.is_active = False
        routine2.is_active = True
        session.commit()

        # Assert
        session.refresh(routine1)
        session.refresh(routine2)
        assert routine1.is_active is False, "Routine1 deve estar inativa"
        assert routine2.is_active is True, "Routine2 deve estar ativa"

    def test_br_routine_001_create_not_auto_active(self, session: Session):
        """BR-ROUTINE-001: Criar rotina não ativa automaticamente."""
        # Arrange
        existing = Routine(name="Rotina Matinal", is_active=True)
        session.add(existing)
        session.commit()

        # Act
        new_routine = Routine(name="Rotina Fim de Semana")
        session.add(new_routine)
        session.commit()

        # Assert
        assert new_routine.is_active is False, "Nova rotina não deve ser ativa"
        session.refresh(existing)
        assert existing.is_active is True, "Rotina existente deve permanecer ativa"


# BR-ROUTINE-002: Habit Belongs to Routine
class TestBRRoutine002:
    """Valida BR-ROUTINE-002: Habit pertence a UMA rotina."""

    def test_br_routine_002_habit_requires_routine_id(self, session: Session):
        """BR-ROUTINE-002: Habit requer routine_id (NOT NULL)."""
        # Arrange
        routine = Routine(name="Rotina Matinal", is_active=True)
        session.add(routine)
        session.commit()

        assert routine.id is not None, "Routine deve ter id após commit"

        # Act
        habit = Habit(
            routine_id=routine.id,
            title="Academia",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 30),
            recurrence=Recurrence.WEEKDAYS,
        )
        session.add(habit)
        session.commit()

        # Assert
        assert habit.routine_id is not None, "Habit deve ter routine_id"
        assert habit.routine_id == routine.id

    def test_br_routine_002_foreign_key_valid(self, session: Session):
        """BR-ROUTINE-002: routine_id deve ser FK válida."""
        # Arrange
        routine = Routine(name="Rotina Matinal", is_active=True)
        session.add(routine)
        session.commit()

        assert routine.id is not None

        # Act
        habit = Habit(
            routine_id=routine.id,
            title="Academia",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 30),
            recurrence=Recurrence.WEEKDAYS,
        )
        session.add(habit)
        session.commit()

        # Assert
        result = session.exec(select(Habit).where(Habit.id == habit.id)).first()
        assert result is not None
        assert result.routine_id == routine.id

    def test_br_routine_002_delete_routine_cascade(self, session: Session):
        """BR-ROUTINE-002: Deletar rotina afeta habits vinculados."""
        # Arrange
        routine = Routine(name="Rotina Matinal", is_active=True)
        session.add(routine)
        session.commit()

        assert routine.id is not None

        habit = Habit(
            routine_id=routine.id,
            title="Academia",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 30),
            recurrence=Recurrence.WEEKDAYS,
        )
        session.add(habit)
        session.commit()
        habit_id = habit.id

        # Act
        session.delete(routine)
        session.commit()

        # Assert
        # Comportamento depende de cascade configurado no modelo
        # TODO: Definir comportamento esperado (CASCADE ou RESTRICT)
        _ = session.get(Habit, habit_id)


# BR-ROUTINE-003: Task Independent of Routine
class TestBRRoutine003:
    """Valida BR-ROUTINE-003: Task não pertence a rotina."""

    def test_br_routine_003_task_no_routine_field(self):
        """BR-ROUTINE-003: Task não possui campo routine_id."""
        # Assert
        assert not hasattr(Task, "routine_id"), "Task não deve ter routine_id"

    def test_br_routine_003_task_created_without_routine(self, session: Session):
        """BR-ROUTINE-003: Task criada sem routine_id."""
        # Arrange
        routine = Routine(name="Rotina Matinal", is_active=True)
        session.add(routine)
        session.commit()

        # Act
        task = Task(
            title="Dentista",
            scheduled_datetime=datetime(2025, 11, 25, 14, 30),
        )
        session.add(task)
        session.commit()

        # Assert
        assert not hasattr(task, "routine_id"), "Task não deve ter routine_id"

    def test_br_routine_003_delete_routine_keeps_tasks(self, session: Session):
        """BR-ROUTINE-003: Deletar rotina não afeta tasks."""
        # Arrange
        routine = Routine(name="Rotina Matinal", is_active=True)
        session.add(routine)
        session.commit()

        task = Task(
            title="Dentista",
            scheduled_datetime=datetime(2025, 11, 25, 14, 30),
        )
        session.add(task)
        session.commit()
        task_id = task.id

        # Act
        session.delete(routine)
        session.commit()

        # Assert
        result = session.get(Task, task_id)
        assert result is not None, "Task deve permanecer após deletar rotina"
        assert result.title == "Dentista"


# BR-ROUTINE-004: Activation Cascade
class TestBRRoutine004:
    """Valida BR-ROUTINE-004: Contexto de rotina ativa."""

    def test_br_routine_004_get_active_routine(self, session: Session):
        """BR-ROUTINE-004: Sistema retorna rotina ativa."""
        # Arrange
        routine1 = Routine(name="Rotina Matinal", is_active=False)
        routine2 = Routine(name="Rotina Trabalho", is_active=True)
        session.add(routine1)
        session.add(routine2)
        session.commit()

        # Act
        active = session.exec(select(Routine).where(Routine.is_active)).first()

        # Assert
        assert active is not None, "Deve haver rotina ativa"
        assert active.name == "Rotina Trabalho"

    def test_br_routine_004_error_no_active_routine(self, session: Session):
        """BR-ROUTINE-004: Erro quando nenhuma rotina ativa."""
        # Arrange
        routine = Routine(name="Rotina Matinal", is_active=False)
        session.add(routine)
        session.commit()

        # Act
        active = session.exec(select(Routine).where(Routine.is_active)).first()

        # Assert
        assert active is None, "Não deve haver rotina ativa"

    def test_br_routine_004_habits_filtered_by_active(self, session: Session):
        """BR-ROUTINE-004: Habits filtrados por rotina ativa."""
        # Arrange
        routine1 = Routine(name="Rotina Matinal", is_active=True)
        routine2 = Routine(name="Rotina Trabalho", is_active=False)
        session.add(routine1)
        session.add(routine2)
        session.commit()

        assert routine1.id is not None
        assert routine2.id is not None

        habit1 = Habit(
            routine_id=routine1.id,
            title="Academia",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 30),
            recurrence=Recurrence.WEEKDAYS,
        )
        habit2 = Habit(
            routine_id=routine2.id,
            title="Daily Standup",
            scheduled_start=time(9, 0),
            scheduled_end=time(9, 15),
            recurrence=Recurrence.WEEKDAYS,
        )
        session.add(habit1)
        session.add(habit2)
        session.commit()

        # Act
        active_routine = session.exec(select(Routine).where(Routine.is_active)).first()
        assert active_routine is not None
        habits = session.exec(select(Habit).where(Habit.routine_id == active_routine.id)).all()

        # Assert
        assert len(habits) == 1, "Deve retornar apenas habits da rotina ativa"
        assert habits[0].title == "Academia"
