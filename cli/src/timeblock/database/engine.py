"""Database connection and operations."""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from sqlalchemy import event
from sqlmodel import SQLModel, create_engine


def get_db_path() -> str:
    """Get database path from environment or default."""
    db_path = os.getenv("TIMEBLOCK_DB_PATH")
    if db_path is None:
        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        db_path = str(data_dir / "timeblock.db")
    return db_path


def get_engine():
    """Get SQLite engine with foreign keys enabled."""
    db_path = get_db_path()
    engine = create_engine(f"sqlite:///{db_path}", echo=False)

    # Habilitar foreign keys no SQLite (CRÍTICO para RESTRICT)
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn: Any, connection_record: Any) -> None:
        """Habilita foreign keys no SQLite."""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


@contextmanager
def get_engine_context():
    """Get SQLite engine with automatic cleanup."""
    engine = get_engine()
    try:
        yield engine
    finally:
        engine.dispose()


def create_db_and_tables():
    """Create database tables."""
    with get_engine_context() as engine:
        SQLModel.metadata.create_all(engine)
    return engine
