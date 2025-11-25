"""Testes de integração para logging nos services."""

import tempfile
from datetime import date, time, timedelta
from pathlib import Path

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models import Habit, Recurrence, Routine
from src.timeblock.services.habit_instance_service import HabitInstanceService
from src.timeblock.utils.logger import disable_logging, enable_logging, setup_logger


@pytest.fixture
def test_engine():
    """Engine SQLite em memória para testes isolados."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def mock_engine(monkeypatch, test_engine):
    """Mock get_engine_context para usar banco de teste."""
    from contextlib import contextmanager

    @contextmanager
    def mock_get_engine():
        yield test_engine

    monkeypatch.setattr(
        "src.timeblock.services.habit_instance_service.get_engine_context", mock_get_engine
    )


@pytest.fixture
def habit(test_engine):
    """Cria hábito de teste."""
    with Session(test_engine) as session:
        routine = Routine(name="Test Routine")
        session.add(routine)
        session.commit()
        session.refresh(routine)

        habit = Habit(
            routine_id=routine.id,
            title="Test Habit",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)
        return habit


class TestServiceLogging:
    """Testa logs gerados pelos services."""

    def test_generate_instances_logs(self, habit):
        """Verifica logs ao gerar instâncias.

        DADO: Hábito válido
        QUANDO: Gerar instâncias
        ENTÃO: Deve logar início, sucesso e quantidade criada
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "service.log"

            # Preparação: Configura logging para arquivo
            setup_logger(
                "src.timeblock.services.habit_instance_service",
                level="INFO",
                log_file=log_file,
                console=False,
            )

            # Ação: Gera instâncias
            start = date.today()
            end = start + timedelta(days=6)
            instances = HabitInstanceService.generate_instances(habit.id, start, end)

            # Verificação: Logs contêm informações esperadas
            content = log_file.read_text()
            assert "Gerando instâncias" in content
            assert f"habit_id={habit.id}" in content
            assert "Criadas 7 instâncias" in content

    def test_mark_completed_logs(self, habit):
        """Verifica logs ao completar instância.

        DADO: Instância válida
        QUANDO: Marcar como completa
        ENTÃO: Deve logar sucesso
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "service.log"

            # Preparação: Cria instância e configura logging
            instances = HabitInstanceService.generate_instances(
                habit.id, date.today(), date.today()
            )
            instance_id = instances[0].id

            setup_logger(
                "src.timeblock.services.habit_instance_service",
                level="INFO",
                log_file=log_file,
                console=False,
            )

            # Ação: Completa instância
            HabitInstanceService.mark_completed(instance_id)

            # Verificação: Log de sucesso
            content = log_file.read_text()
            assert "Instância completada" in content
            assert f"instance_id={instance_id}" in content

    def test_error_logs(self):
        """Verifica logs de erro ao tentar operação inválida.

        DADO: habit_id inexistente
        QUANDO: Tentar gerar instâncias
        ENTÃO: Deve logar erro antes de levantar exceção
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "service.log"

            # Preparação: Configura logging
            setup_logger(
                "src.timeblock.services.habit_instance_service",
                level="ERROR",
                log_file=log_file,
                console=False,
            )

            # Ação: Tenta gerar para hábito inexistente
            with pytest.raises(ValueError):
                HabitInstanceService.generate_instances(99999, date.today(), date.today())

            # Verificação: Log de erro
            content = log_file.read_text()
            assert "Hábito não encontrado" in content
            assert "habit_id=99999" in content

    def test_warning_logs(self, habit):
        """Verifica logs de warning em operações suspeitas.

        DADO: instance_id inexistente
        QUANDO: Tentar marcar como completa
        ENTÃO: Deve logar warning (não erro, pois retorna None)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "service.log"

            # Preparação: Configura logging
            setup_logger(
                "src.timeblock.services.habit_instance_service",
                level="WARNING",
                log_file=log_file,
                console=False,
            )

            # Ação: Tenta completar instância inexistente
            result = HabitInstanceService.mark_completed(99999)

            # Verificação: Retorna None e loga warning
            assert result is None
            content = log_file.read_text()
            assert "inexistente" in content
            assert "instance_id=99999" in content


class TestLoggingInTests:
    """Testa comportamento de logging durante testes."""

    def test_logs_disabled_by_default_in_tests(self, habit):
        """Logs não aparecem no console durante testes normais.

        DADO: Suite de testes rodando
        QUANDO: Service executa operação
        ENTÃO: Logs não devem poluir output de teste

        Nota: Este teste verifica que logs podem ser silenciados.
        """
        # Ação: Desabilita logging
        disable_logging()

        # Executa operação (sem logs no console)
        instances = HabitInstanceService.generate_instances(habit.id, date.today(), date.today())

        # Verificação: Operação funcionou
        assert len(instances) == 1

        # Limpeza: Reabilita
        enable_logging()
