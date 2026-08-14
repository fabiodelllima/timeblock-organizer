"""Migração 005: horário planejado em HabitInstance (BR-HABITINSTANCE-008).

Adiciona original_scheduled_start, original_scheduled_end e adjustment_count à
tabela habitinstance, e faz backfill das linhas existentes a partir do horário
corrente — para linhas anteriores a esta migração, plano e execução são
indistinguíveis, e igualá-los é a única leitura honesta disponível.

Referências:
    - BR-HABITINSTANCE-008: Preservação do Horário Planejado
    - BR-TASK-008: precedente de horário original imutável com contador
"""

from sqlalchemy import text
from sqlmodel import Session


def upgrade(session: Session) -> None:
    """Aplica migração: adiciona as três colunas e faz backfill."""
    conn = session.connection()

    result = conn.execute(text("PRAGMA table_info(habitinstance)"))
    columns = {row[1] for row in result}

    if "original_scheduled_start" not in columns:
        conn.execute(text("ALTER TABLE habitinstance ADD COLUMN original_scheduled_start TIME"))

    if "original_scheduled_end" not in columns:
        conn.execute(text("ALTER TABLE habitinstance ADD COLUMN original_scheduled_end TIME"))

    if "adjustment_count" not in columns:
        conn.execute(
            text("ALTER TABLE habitinstance ADD COLUMN adjustment_count INTEGER DEFAULT 0")
        )

    conn.execute(
        text(
            "UPDATE habitinstance "
            "SET original_scheduled_start = scheduled_start "
            "WHERE original_scheduled_start IS NULL"
        )
    )
    conn.execute(
        text(
            "UPDATE habitinstance "
            "SET original_scheduled_end = scheduled_end "
            "WHERE original_scheduled_end IS NULL"
        )
    )
    conn.execute(
        text("UPDATE habitinstance SET adjustment_count = 0 WHERE adjustment_count IS NULL")
    )

    session.commit()


def downgrade(session: Session) -> None:
    """Reverte migração (SQLite não suporta DROP COLUMN < 3.35)."""
    pass
