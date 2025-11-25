"""
Factories para criação de objetos de teste.

Este módulo implementa o Factory Pattern para gerar objetos de teste
com valores padrão sensatos, permitindo overrides quando necessário.

Uso:
    # Usar valores padrão
    habit = HabitFactory.create()

    # Override valores específicos
    habit = HabitFactory.create(title="Meditação", scheduled_start=time(6, 0))

Referências:
    - Pattern: Factory Method (GoF Design Patterns)
    - ADR-019: Test Naming Convention
"""

from datetime import date, datetime, time
from typing import Any

from src.timeblock.models import (
    Habit,
    HabitInstance,
    Recurrence,
    Routine,
    Tag,
    Task,
)


class RoutineFactory:
    """Factory para criar Routines de teste."""

    _sequence = 0

    @classmethod
    def create(cls, **overrides: Any) -> Routine:
        """
        Cria Routine com valores padrão.

        Args:
            **overrides: Valores para sobrescrever padrões

        Returns:
            Routine: Instância com valores padrão + overrides

        Exemplo:
            >>> routine = RoutineFactory.create()
            >>> routine.name
            'Rotina Teste 1'
            >>> routine.is_active
            True
        """
        cls._sequence += 1

        defaults = {
            "name": f"Rotina Teste {cls._sequence}",
            "is_active": True,
        }
        defaults.update(overrides)
        return Routine(**defaults)

    @classmethod
    def reset_sequence(cls) -> None:
        """Reseta contador de sequência (útil entre testes)."""
        cls._sequence = 0


class HabitFactory:
    """Factory para criar Habits de teste."""

    _sequence = 0

    @classmethod
    def create(cls, **overrides: Any) -> Habit:
        """
        Cria Habit com valores padrão.

        Args:
            **overrides: Valores para sobrescrever padrões
                routine_id: ID da rotina (padrão: 1)
                title: Título do hábito (padrão: "Hábito Teste N")
                scheduled_start: Horário início (padrão: 06:00)
                scheduled_end: Horário fim (padrão: 07:00)
                recurrence: Padrão recorrência (padrão: EVERYDAY)
                color: Cor (padrão: None)

        Returns:
            Habit: Instância com valores padrão + overrides

        Exemplo:
            >>> habit = HabitFactory.create(title="Meditar")
            >>> habit.scheduled_start
            time(6, 0)
        """
        cls._sequence += 1

        defaults = {
            "routine_id": 1,
            "title": f"Hábito Teste {cls._sequence}",
            "scheduled_start": time(6, 0),
            "scheduled_end": time(7, 0),
            "recurrence": Recurrence.EVERYDAY,
            "color": None,
        }
        defaults.update(overrides)
        return Habit(**defaults)

    @classmethod
    def reset_sequence(cls) -> None:
        """Reseta contador de sequência."""
        cls._sequence = 0


class HabitInstanceFactory:
    """Factory para criar HabitInstances de teste."""

    _sequence = 0

    @classmethod
    def create(cls, **overrides: Any) -> HabitInstance:
        """
        Cria HabitInstance com valores padrão.

        Args:
            **overrides: Valores para sobrescrever padrões
                habit_id: ID do hábito (padrão: 1)
                date: Data da instância (padrão: hoje)
                scheduled_start: Horário início (padrão: 06:00)
                scheduled_end: Horário fim (padrão: 07:00)
                is_completed: Status (padrão: False)

        Returns:
            HabitInstance: Instância com valores padrão + overrides
        """
        cls._sequence += 1

        defaults = {
            "habit_id": 1,
            "date": date.today(),
            "scheduled_start": time(6, 0),
            "scheduled_end": time(7, 0),
            "is_completed": False,
        }
        defaults.update(overrides)
        return HabitInstance(**defaults)

    @classmethod
    def reset_sequence(cls) -> None:
        """Reseta contador de sequência."""
        cls._sequence = 0


class TaskFactory:
    """Factory para criar Tasks de teste."""

    _sequence = 0

    @classmethod
    def create(cls, **overrides: Any) -> Task:
        """
        Cria Task com valores padrão.

        Args:
            **overrides: Valores para sobrescrever padrões
                title: Título da task (padrão: "Task Teste N")
                scheduled_datetime: Data/hora (padrão: hoje 10:00)
                duration_minutes: Duração (padrão: 60)
                is_completed: Status (padrão: False)

        Returns:
            Task: Instância com valores padrão + overrides
        """
        cls._sequence += 1

        defaults = {
            "title": f"Task Teste {cls._sequence}",
            "scheduled_datetime": datetime.combine(date.today(), time(10, 0)),
            "duration_minutes": 60,
            "is_completed": False,
        }
        defaults.update(overrides)
        return Task(**defaults)

    @classmethod
    def reset_sequence(cls) -> None:
        """Reseta contador de sequência."""
        cls._sequence = 0


class TagFactory:
    """Factory para criar Tags de teste."""

    _sequence = 0

    @classmethod
    def create(cls, **overrides: Any) -> Tag:
        """
        Cria Tag com valores padrão.

        Args:
            **overrides: Valores para sobrescrever padrões
                name: Nome da tag (padrão: "Tag Teste N")
                color: Cor (padrão: "#FF5733")

        Returns:
            Tag: Instância com valores padrão + overrides
        """
        cls._sequence += 1

        defaults = {
            "name": f"Tag Teste {cls._sequence}",
            "color": "#FF5733",
        }
        defaults.update(overrides)
        return Tag(**defaults)

    @classmethod
    def reset_sequence(cls) -> None:
        """Reseta contador de sequência."""
        cls._sequence = 0


def reset_all_sequences() -> None:
    """
    Reseta contadores de todas factories.

    Útil no teardown de testes para garantir IDs consistentes
    entre execuções.
    """
    RoutineFactory.reset_sequence()
    HabitFactory.reset_sequence()
    HabitInstanceFactory.reset_sequence()
    TaskFactory.reset_sequence()
    TagFactory.reset_sequence()
