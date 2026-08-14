"""Migration runner — executa migrações pendentes no startup.

Verifica quais migrações já foram aplicadas usando a tabela
schema_migrations e executa as pendentes em ordem.

Referências:
    - ADR-026: Database path via engine.get_db_path() (SSOT)
"""

import logging

from sqlalchemy import text
from sqlmodel import Session

from timeblock.database.engine import get_engine

logger = logging.getLogger(__name__)

# Registro ordenado de migrações disponíveis
MIGRATIONS: list[tuple[str, str]] = [
    ("002", "timeblock.database.migrations.migration_002_task_lifecycle"),
    ("003", "timeblock.database.migrations.migration_003_best_streak"),
    ("004", "timeblock.database.migrations.migration_004_habit_archive"),
    ("005", "timeblock.database.migrations.migration_005_habitinstance_planned_time"),
]


def _ensure_schema_migrations(session: Session) -> None:
    """Garante que a tabela schema_migrations existe."""
    session.execute(
        text(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  migration_id VARCHAR(10) NOT NULL UNIQUE,"
            "  applied_at DATETIME DEFAULT CURRENT_TIMESTAMP"
            ")"
        )
    )
    session.commit()


def _applied_migrations(session: Session) -> set[str]:
    """Retorna IDs de migrações já aplicadas."""
    result = session.execute(text("SELECT migration_id FROM schema_migrations"))
    return {row[0] for row in result}


def run_pending_migrations() -> int:
    """Executa migrações pendentes. Retorna quantidade aplicada."""
    engine = get_engine()
    applied_count = 0

    with Session(engine) as session:
        _ensure_schema_migrations(session)
        applied = _applied_migrations(session)

        for migration_id, module_path in MIGRATIONS:
            if migration_id in applied:
                continue

            try:
                import importlib

                mod = importlib.import_module(module_path)
                mod.upgrade(session)

                session.execute(
                    text("INSERT INTO schema_migrations (migration_id) VALUES (:mid)"),
                    {"mid": migration_id},
                )
                session.commit()

                applied_count += 1
                logger.info("Migração %s aplicada", migration_id)

            except Exception:
                session.rollback()
                logger.exception("Falha na migração %s", migration_id)
                raise

    engine.dispose()
    return applied_count
