"""Migration: adiciona started_at, color, tag_id ao Task."""

import sqlite3
from pathlib import Path


def find_db():
    """Localiza banco de dados."""
    paths = [
        Path.home() / ".config/timeblock/timeblock.db",
        Path.home() / ".timeblock/timeblock.db",
        Path("timeblock.db"),
    ]
    for p in paths:
        if p.exists():
            return p
    raise FileNotFoundError(f"DB não encontrado em: {paths}")


def migrate():
    """Adiciona colunas ao Task."""
    db = find_db()
    print(f"DB: {db}")

    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(task)")
        cols = {row[1] for row in cursor.fetchall()}

        adds = []
        if "started_at" not in cols:
            adds.append(("started_at", "TIMESTAMP"))
        if "color" not in cols:
            adds.append(("color", "VARCHAR"))
        if "tag_id" not in cols:
            adds.append(("tag_id", "INTEGER"))

        if not adds:
            print("✓ Colunas já existem")
            return

        for col, typ in adds:
            sql = f"ALTER TABLE task ADD COLUMN {col} {typ}"
            print(f"+ {sql}")
            cursor.execute(sql)

        conn.commit()
        print(f"✓ {len(adds)} coluna(s) adicionada(s)")

    except sqlite3.Error as e:
        conn.rollback()
        print(f"✗ Erro: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
