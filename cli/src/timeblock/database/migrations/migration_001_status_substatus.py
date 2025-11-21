"""Migração 001: Refatoração Status+Substatus (BR-HABIT-INSTANCE-STATUS-001).

Adiciona novos campos ao HabitInstance:
- done_substatus
- not_done_substatus
- skip_reason
- skip_note
- completion_percentage

Migra dados existentes de status antigo (string) para novo (enum).
"""

from sqlalchemy import text
from sqlmodel import Session


def upgrade(session: Session) -> None:
    """Aplica migração: adiciona colunas e migra dados.

    Args:
        session: Sessão do banco de dados
    """
    # 1. Adicionar novas colunas
    session.exec(
        text("""
        ALTER TABLE habitinstance 
        ADD COLUMN done_substatus VARCHAR(50) DEFAULT NULL
    """)
    )

    session.exec(
        text("""
        ALTER TABLE habitinstance 
        ADD COLUMN not_done_substatus VARCHAR(50) DEFAULT NULL
    """)
    )

    session.exec(
        text("""
        ALTER TABLE habitinstance 
        ADD COLUMN skip_reason VARCHAR(50) DEFAULT NULL
    """)
    )

    session.exec(
        text("""
        ALTER TABLE habitinstance 
        ADD COLUMN skip_note TEXT DEFAULT NULL
    """)
    )

    session.exec(
        text("""
        ALTER TABLE habitinstance 
        ADD COLUMN completion_percentage INTEGER DEFAULT NULL
    """)
    )

    # 2. Criar coluna temporária para novo status
    session.exec(
        text("""
        ALTER TABLE habitinstance 
        ADD COLUMN status_new VARCHAR(20) DEFAULT NULL
    """)
    )

    # 3. Migrar dados de status antigo -> novo
    # PLANNED -> pending
    session.exec(
        text("""
        UPDATE habitinstance 
        SET status_new = 'pending' 
        WHERE status = 'PLANNED'
    """)
    )

    # IN_PROGRESS -> pending
    session.exec(
        text("""
        UPDATE habitinstance 
        SET status_new = 'pending' 
        WHERE status = 'IN_PROGRESS'
    """)
    )

    # PAUSED -> pending
    session.exec(
        text("""
        UPDATE habitinstance 
        SET status_new = 'pending' 
        WHERE status = 'PAUSED'
    """)
    )

    # COMPLETED -> done (assumir FULL se não tiver info de completion)
    session.exec(
        text("""
        UPDATE habitinstance 
        SET status_new = 'done',
            done_substatus = 'full'
        WHERE status = 'COMPLETED'
    """)
    )

    # SKIPPED -> not_done (assumir UNJUSTIFIED se não tiver categoria)
    session.exec(
        text("""
        UPDATE habitinstance 
        SET status_new = 'not_done',
            not_done_substatus = 'skipped_unjustified'
        WHERE status = 'SKIPPED'
    """)
    )

    # 4. Remover coluna antiga e renomear nova
    session.exec(
        text("""
        ALTER TABLE habitinstance DROP COLUMN status
    """)
    )

    session.exec(
        text("""
        ALTER TABLE habitinstance 
        RENAME COLUMN status_new TO status
    """)
    )

    # 5. Definir default para status
    session.exec(
        text("""
        UPDATE habitinstance 
        SET status = 'pending' 
        WHERE status IS NULL
    """)
    )

    session.commit()


def downgrade(session: Session) -> None:
    """Reverte migração: remove colunas e restaura status antigo.

    Args:
        session: Sessão do banco de dados
    """
    # 1. Criar coluna status antiga
    session.exec(
        text("""
        ALTER TABLE habitinstance 
        ADD COLUMN status_old VARCHAR(20) DEFAULT NULL
    """)
    )

    # 2. Migrar dados de volta (novo -> antigo)
    # pending -> PLANNED
    session.exec(
        text("""
        UPDATE habitinstance 
        SET status_old = 'PLANNED' 
        WHERE status = 'pending'
    """)
    )

    # done -> COMPLETED
    session.exec(
        text("""
        UPDATE habitinstance 
        SET status_old = 'COMPLETED' 
        WHERE status = 'done'
    """)
    )

    # not_done -> SKIPPED
    session.exec(
        text("""
        UPDATE habitinstance 
        SET status_old = 'SKIPPED' 
        WHERE status = 'not_done'
    """)
    )

    # 3. Remover coluna nova e renomear antiga
    session.exec(
        text("""
        ALTER TABLE habitinstance DROP COLUMN status
    """)
    )

    session.exec(
        text("""
        ALTER TABLE habitinstance 
        RENAME COLUMN status_old TO status
    """)
    )

    # 4. Remover colunas novas
    session.exec(
        text("""
        ALTER TABLE habitinstance DROP COLUMN done_substatus
    """)
    )

    session.exec(
        text("""
        ALTER TABLE habitinstance DROP COLUMN not_done_substatus
    """)
    )

    session.exec(
        text("""
        ALTER TABLE habitinstance DROP COLUMN skip_reason
    """)
    )

    session.exec(
        text("""
        ALTER TABLE habitinstance DROP COLUMN skip_note
    """)
    )

    session.exec(
        text("""
        ALTER TABLE habitinstance DROP COLUMN completion_percentage
    """)
    )

    session.commit()


# Metadata para controle de versão
MIGRATION_VERSION = "001"
MIGRATION_NAME = "status_substatus_refactoring"
MIGRATION_DESCRIPTION = "Refatoração Status+Substatus (BR-HABIT-INSTANCE-STATUS-001)"
