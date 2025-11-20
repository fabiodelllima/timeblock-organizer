"""Teste para propriedade is_overdue de HabitInstance."""

from datetime import date, time

import pytest
from freezegun import freeze_time
from sqlmodel import SQLModel, create_engine

from src.timeblock.models import HabitInstance, Status


@pytest.fixture
def test_engine():
    """Engine SQLite em memória."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


class TestHabitInstanceOverdue:
    """
    REGRA DE NEGÓCIO RN023: Propriedade is_overdue
    
    A propriedade is_overdue deve retornar True quando:
    1. Status é PLANNED
    2. Hora atual > scheduled_start
    
    Deve retornar False para qualquer outro status.
    """

    def test_overdue_when_planned_and_past_time(self):
        """
        CENÁRIO: HabitInstance planejado com horário passado
        DADO: Uma instância com status PLANNED para às 8h
        QUANDO: São 9h do mesmo dia
        ENTÃO: is_overdue deve ser True
        """
        # Arrange
        instance = HabitInstance(
            id=1,
            habit_id=1,
            date=date(2025, 10, 25),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.PLANNED,
            manually_adjusted=False,
            user_override=False
        )

        # Act - Congelar tempo às 9h
        with freeze_time("2025-10-25 09:00:00"):
            result = instance.is_overdue

        # Assert
        assert result is True, "Instância PLANNED após horário deve ser overdue"

    def test_not_overdue_when_planned_and_future_time(self):
        """
        CENÁRIO: HabitInstance planejado com horário futuro
        DADO: Uma instância com status PLANNED para às 14h
        QUANDO: São 9h do mesmo dia
        ENTÃO: is_overdue deve ser False
        """
        # Arrange
        instance = HabitInstance(
            id=2,
            habit_id=1,
            date=date(2025, 10, 25),
            scheduled_start=time(14, 0),
            scheduled_end=time(15, 0),
            status=Status.PLANNED,
            manually_adjusted=False,
            user_override=False
        )

        # Act
        with freeze_time("2025-10-25 09:00:00"):
            result = instance.is_overdue

        # Assert
        assert result is False, "Instância PLANNED no futuro não é overdue"

    def test_not_overdue_when_in_progress(self):
        """
        CENÁRIO: HabitInstance em progresso
        DADO: Uma instância com status IN_PROGRESS
        QUANDO: Qualquer horário
        ENTÃO: is_overdue deve ser False
        """
        # Arrange
        instance = HabitInstance(
            id=3,
            habit_id=1,
            date=date(2025, 10, 25),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.IN_PROGRESS,
            manually_adjusted=False,
            user_override=False
        )

        # Act - Mesmo após o horário
        with freeze_time("2025-10-25 10:00:00"):
            result = instance.is_overdue

        # Assert
        assert result is False, "IN_PROGRESS nunca é overdue"

    def test_not_overdue_when_completed(self):
        """
        CENÁRIO: HabitInstance completado
        DADO: Uma instância com status COMPLETED
        QUANDO: Qualquer horário
        ENTÃO: is_overdue deve ser False
        """
        # Arrange
        instance = HabitInstance(
            id=4,
            habit_id=1,
            date=date(2025, 10, 25),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.COMPLETED,
            manually_adjusted=False,
            user_override=False
        )

        # Act
        with freeze_time("2025-10-25 20:00:00"):
            result = instance.is_overdue

        # Assert
        assert result is False, "COMPLETED nunca é overdue"

    def test_not_overdue_when_skipped(self):
        """
        CENÁRIO: HabitInstance pulado
        DADO: Uma instância com status SKIPPED
        QUANDO: Qualquer horário
        ENTÃO: is_overdue deve ser False
        """
        # Arrange
        instance = HabitInstance(
            id=5,
            habit_id=1,
            date=date(2025, 10, 25),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.SKIPPED,
            manually_adjusted=False,
            user_override=False
        )

        # Act
        with freeze_time("2025-10-25 20:00:00"):
            result = instance.is_overdue

        # Assert
        assert result is False, "SKIPPED nunca é overdue"

    def test_overdue_one_minute_after(self):
        """
        CENÁRIO: Um minuto após o horário
        DADO: Uma instância PLANNED para às 14:00
        QUANDO: São 14:01
        ENTÃO: is_overdue deve ser True
        """
        # Arrange
        instance = HabitInstance(
            id=6,
            habit_id=1,
            date=date(2025, 10, 25),
            scheduled_start=time(14, 0),
            scheduled_end=time(15, 0),
            status=Status.PLANNED,
            manually_adjusted=False,
            user_override=False
        )

        # Act
        with freeze_time("2025-10-25 14:01:00"):
            result = instance.is_overdue

        # Assert
        assert result is True, "1 minuto após já é overdue"
