"""Configuration management."""
import os
from pathlib import Path

# Database path
_db_path_env = os.getenv("TIMEBLOCK_DB_PATH")
if _db_path_env:
    DATABASE_PATH = Path(_db_path_env)
else:
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    DATABASE_PATH = data_dir / "timeblock.db"
