"""Database migrations for v2.0."""

from pathlib import Path

from sqlmodel import SQLModel, create_engine

from ..config import DATABASE_PATH
from ..models import Habit, HabitInstance, Routine, Task, TimeLog


def migrate_v2(db_path: Path | None = None) -> None:
    """Adiciona tabelas v2.0."""
    path = db_path or DATABASE_PATH
    engine = create_engine(f"sqlite:///{path}")

    # Criar novas tabelas
    SQLModel.metadata.create_all(
        engine,
        tables=[
            Routine.__table__,
            Habit.__table__,
            HabitInstance.__table__,
            Task.__table__,
            TimeLog.__table__,
        ],
    )

    print("✓ Tabelas v2.0 criadas: Routine, Habit, HabitInstance, Task, TimeLog")


def migrate_events_to_tasks() -> int:
    """Migra Events existentes para Tasks (opcional)."""
    # TODO: Implementar em próxima fase
    return 0
