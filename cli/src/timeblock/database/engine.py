"""Database connection and operations."""

import os
from contextlib import contextmanager
from pathlib import Path

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
    """Get SQLite engine."""
    db_path = get_db_path()
    return create_engine(f"sqlite:///{db_path}", echo=False)


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
