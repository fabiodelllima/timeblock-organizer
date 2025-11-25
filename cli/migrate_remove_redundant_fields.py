#!/usr/bin/env python3
"""
Migration: Remove campos redundantes de HabitInstance.

Campos removidos:
- manually_adjusted: redundante, pode ser detectado comparando horários
- user_override: redundante, mesma função que manually_adjusted

Data: 07 de Novembro de 2025
Sprint 4: Migration e Modelo
"""

import sqlite3
from pathlib import Path


def migrate_database(db_path: str) -> None:
    """Remove campos redundantes da tabela habitinstance."""
    print(f"Migrando banco de dados: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Verificar se as colunas existem
        cursor.execute("PRAGMA table_info(habitinstance)")
        columns = [row[1] for row in cursor.fetchall()]

        has_manually_adjusted = "manually_adjusted" in columns
        has_user_override = "user_override" in columns

        if not has_manually_adjusted and not has_user_override:
            print("✓ Colunas já foram removidas. Nada a fazer.")
            return

        print("Iniciando migration...")

        # SQLite não suporta DROP COLUMN diretamente
        # Precisamos criar nova tabela e copiar dados

        # 1. Criar nova tabela sem os campos redundantes
        cursor.execute("""
            CREATE TABLE habitinstance_new (
                id INTEGER PRIMARY KEY,
                habit_id INTEGER NOT NULL,
                date DATE NOT NULL,
                scheduled_start TIME NOT NULL,
                scheduled_end TIME NOT NULL,
                status TEXT NOT NULL DEFAULT 'PLANNED',
                FOREIGN KEY (habit_id) REFERENCES habits(id)
            )
        """)
        print("✓ Nova tabela criada")

        # 2. Criar índice na nova tabela
        cursor.execute("""
            CREATE INDEX ix_habitinstance_new_date ON habitinstance_new(date)
        """)
        print("✓ Índice criado")

        # 3. Copiar dados (sem os campos removidos)
        cursor.execute("""
            INSERT INTO habitinstance_new (
                id, habit_id, date, scheduled_start, scheduled_end, status
            )
            SELECT
                id, habit_id, date, scheduled_start, scheduled_end, status
            FROM habitinstance
        """)
        rows_copied = cursor.rowcount
        print(f"✓ {rows_copied} registros copiados")

        # 4. Dropar tabela antiga
        cursor.execute("DROP TABLE habitinstance")
        print("✓ Tabela antiga removida")

        # 5. Renomear nova tabela
        cursor.execute("ALTER TABLE habitinstance_new RENAME TO habitinstance")
        print("✓ Tabela renomeada")

        # Commit
        conn.commit()
        print("\n✓ Migration concluída com sucesso!")

    except Exception as e:
        conn.rollback()
        print(f"\n✗ Erro durante migration: {e}")
        raise

    finally:
        conn.close()


def main():
    """Executa migration em todos os bancos encontrados."""
    # Buscar bancos de dados
    databases = [
        "cli/data/timeblock.db",
        "cli/src/data/timeblock.db",
        "cli/timeblock.db",
    ]

    found = False
    for db_path in databases:
        if Path(db_path).exists():
            found = True
            print(f"\n{'=' * 60}")
            migrate_database(db_path)
            print("=" * 60)

    if not found:
        print("⚠ Nenhum banco de dados encontrado.")
        print("Execute este script após criar o banco inicial.")


if __name__ == "__main__":
    main()
