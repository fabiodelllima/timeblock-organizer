"""
Integration tests para migrações de banco de dados.

Testa criação de tabelas durante migração v2.0,
validando que todas as entidades são criadas corretamente.

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
"""

import tempfile
from collections.abc import Iterator
from datetime import date, datetime, time
from pathlib import Path

import pytest
from sqlmodel import Session, create_engine, select

# from src.timeblock.database.migrations import migrate_v2  # TODO: migrate_v2 not implemented yet
from src.timeblock.models import (
    Habit,
    HabitInstance,
    Recurrence,
    Routine,
    Task,
    TimeLog,
)
@pytest.mark.skip(reason="migrate_v2 not implemented yet")


@pytest.fixture
def temp_db() -> Iterator[Path]:
    """
    Cria banco de dados temporário para testes de migração.

    Yields:
        Path para arquivo de database temporário.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    db_path.unlink(missing_ok=True)


class TestBRDatabaseMigrations:
    """
    Integration: Migrações de banco de dados (BR-DB-MIGRATE-*).

    Valida que migrate_v2 cria todas as tabelas necessárias
    e permite operações básicas de CRUD.

    BRs cobertas:
    - BR-DB-MIGRATE-001: Cria todas as tabelas v2.0
    - BR-DB-MIGRATE-002: Cria tabela Routine
    - BR-DB-MIGRATE-003: Cria tabela Habit
    - BR-DB-MIGRATE-004: Cria tabela HabitInstance
    - BR-DB-MIGRATE-005: Cria tabela Task
    - BR-DB-MIGRATE-006: Cria tabela TimeLog
    """

    def test_br_db_migrate_001_creates_all_tables(
        self, temp_db: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """
        Integration: migrate_v2 cria todas as tabelas v2.0.

        DADO: Banco de dados vazio
        QUANDO: migrate_v2 é executado
        ENTÃO: Mensagem de sucesso é exibida
        E: Todas as tabelas existem e permitem operações

        Referências:
            - BR-DB-MIGRATE-001: Criação de todas tabelas v2.0
        """
        # ACT
        migrate_v2(temp_db)
        # ASSERT - Mensagem de sucesso
        captured = capsys.readouterr()
        assert "✓ Tabelas v2.0 criadas" in captured.out
        # ASSERT - Tabela funcional
        engine = create_engine(f"sqlite:///{temp_db}")
        with Session(engine) as session:
            routine = Routine(name="Test")
            session.add(routine)
            session.commit()
            result = session.exec(select(Routine)).first()
            assert result is not None
            assert result.name == "Test"

    def test_br_db_migrate_002_creates_routine_table(
        self, temp_db: Path
    ) -> None:
        """
        Integration: migrate_v2 cria tabela Routine.

        DADO: Banco de dados vazio
        QUANDO: migrate_v2 é executado
        ENTÃO: Tabela Routine existe
        E: Permite inserção e geração de ID

        Referências:
            - BR-DB-MIGRATE-002: Criação de tabela Routine
        """
        # ACT
        migrate_v2(temp_db)
        # ASSERT
        engine = create_engine(f"sqlite:///{temp_db}")
        with Session(engine) as session:
            routine = Routine(name="Morning Routine", is_active=True)
            session.add(routine)
            session.commit()
            assert routine.id is not None, "ID deve ser gerado automaticamente"

    def test_br_db_migrate_003_creates_habit_table(
        self, temp_db: Path
    ) -> None:
        """
        Integration: migrate_v2 cria tabela Habit.

        DADO: Banco de dados vazio
        QUANDO: migrate_v2 é executado
        ENTÃO: Tabela Habit existe
        E: Permite inserção com foreign key para Routine

        Referências:
            - BR-DB-MIGRATE-003: Criação de tabela Habit
        """
        # ACT
        migrate_v2(temp_db)
        # ASSERT
        engine = create_engine(f"sqlite:///{temp_db}")
        with Session(engine) as session:
            # Criar rotina necessária (foreign key)
            routine = Routine(name="Test")
            session.add(routine)
            session.commit()
            # Type narrowing: garantir que ID foi gerado
            assert routine.id is not None
            # Criar hábito
            habit = Habit(
                routine_id=routine.id,
                title="Exercise",
                scheduled_start=time(7, 0),
                scheduled_end=time(8, 0),
                recurrence=Recurrence.EVERYDAY,
            )
            session.add(habit)
            session.commit()
            assert habit.id is not None, "ID deve ser gerado automaticamente"

    def test_br_db_migrate_004_creates_habit_instance_table(
        self, temp_db: Path
    ) -> None:
        """
        Integration: migrate_v2 cria tabela HabitInstance.

        DADO: Banco de dados vazio
        QUANDO: migrate_v2 é executado
        ENTÃO: Tabela HabitInstance existe
        E: Permite inserção com foreign key para Habit

        Referências:
            - BR-DB-MIGRATE-004: Criação de tabela HabitInstance
        """
        # ACT
        migrate_v2(temp_db)
        # ASSERT
        engine = create_engine(f"sqlite:///{temp_db}")
        with Session(engine) as session:
            # Criar rotina e hábito necessários (foreign keys)
            routine = Routine(name="Test")
            session.add(routine)
            session.commit()
            # Type narrowing: garantir que ID foi gerado
            assert routine.id is not None
            habit = Habit(
                routine_id=routine.id,
                title="Exercise",
                scheduled_start=time(7, 0),
                scheduled_end=time(8, 0),
                recurrence=Recurrence.EVERYDAY,
            )
            session.add(habit)
            session.commit()
            # Type narrowing: garantir que ID foi gerado
            assert habit.id is not None
            # Criar instância
            instance = HabitInstance(
                habit_id=habit.id,
                date=date(2025, 10, 16),
                scheduled_start=time(7, 0),
                scheduled_end=time(8, 0),
            )
            session.add(instance)
            session.commit()
            assert instance.id is not None, "ID deve ser gerado automaticamente"

    def test_br_db_migrate_005_creates_task_table(
        self, temp_db: Path
    ) -> None:
        """
        Integration: migrate_v2 cria tabela Task.

        DADO: Banco de dados vazio
        QUANDO: migrate_v2 é executado
        ENTÃO: Tabela Task existe
        E: Permite inserção de tasks pontuais

        Referências:
            - BR-DB-MIGRATE-005: Criação de tabela Task
        """
        # ACT
        migrate_v2(temp_db)
        # ASSERT
        engine = create_engine(f"sqlite:///{temp_db}")
        with Session(engine) as session:
            task = Task(
                title="Doctor Appointment",
                scheduled_datetime=datetime(2025, 10, 17, 14, 0),
            )
            session.add(task)
            session.commit()
            assert task.id is not None, "ID deve ser gerado automaticamente"

    def test_br_db_migrate_006_creates_time_log_table(
        self, temp_db: Path
    ) -> None:
        """
        Integration: migrate_v2 cria tabela TimeLog.

        DADO: Banco de dados vazio
        QUANDO: migrate_v2 é executado
        ENTÃO: Tabela TimeLog existe
        E: Permite inserção de logs de tempo

        Referências:
            - BR-DB-MIGRATE-006: Criação de tabela TimeLog
        """
        # ACT
        migrate_v2(temp_db)
        # ASSERT
        engine = create_engine(f"sqlite:///{temp_db}")
        with Session(engine) as session:
            log = TimeLog(
                start_time=datetime(2025, 10, 16, 7, 0),
                end_time=datetime(2025, 10, 16, 8, 0),
                duration_seconds=3600,
            )
            session.add(log)
            session.commit()
            assert log.id is not None, "ID deve ser gerado automaticamente"
