"""Global pytest configuration."""

import pytest
import os
from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def backup_real_db():
    """Backup real database before tests, restore after."""
    real_db = Path("data/timeblock.db")
    backup = Path("data/timeblock.db.backup")
    
    # Backup if exists
    if real_db.exists():
        real_db.rename(backup)
    
    yield
    
    # Restore
    if backup.exists():
        if real_db.exists():
            real_db.unlink()
        backup.rename(real_db)
