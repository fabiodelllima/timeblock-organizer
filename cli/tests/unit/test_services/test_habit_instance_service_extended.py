"""Testes estendidos para HabitInstanceService - Sprint 1.2 Fase 2.

Estes testes aumentam cobertura de 43% para 83%+ testando:
- Método generate_instances()
- Método mark_completed()
- Método mark_skipped()
"""

from datetime import date, time, timedelta

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models import Habit, Recurrence, Routine, Status
from src.timeblock.services.habit_instance_service import HabitInstanceService


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
def everyday_habit(test_engine):
    """Cria hábito com recorrência EVERYDAY."""
    with Session(test_engine) as session:
        routine = Routine(name="Rotina Matinal")
        session.add(routine)
        session.commit()
        session.refresh(routine)

        habit = Habit(
            routine_id=routine.id,
            title="Exercício Matinal",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)
        return habit


@pytest.fixture
def weekdays_habit(test_engine):
    """Cria hábito com recorrência WEEKDAYS."""
    with Session(test_engine) as session:
        routine = Routine(name="Rotina de Trabalho")
        session.add(routine)
        session.commit()
        session.refresh(routine)

        habit = Habit(
            routine_id=routine.id,
            title="Revisão do Trabalho",
            scheduled_start=time(9, 0),
            scheduled_end=time(9, 30),
            recurrence=Recurrence.WEEKDAYS,
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)
        return habit


class TestGenerateInstances:
    """Testa método generate_instances() - GAP CRÍTICO DE COBERTURA."""

    def test_generate_everyday_habit(self, everyday_habit):
        """Gera instâncias para hábito EVERYDAY durante 7 dias.

        DADO: Hábito com recorrência EVERYDAY
        QUANDO: Gerar instâncias para período de 7 dias
        ENTÃO: Deve criar exatamente 7 instâncias

        Regra de Negócio: Hábitos EVERYDAY geram uma instância por dia.
        """
        # Preparação: Define intervalo de datas
        start = date.today()
        end = start + timedelta(days=6)  # 7 dias total

        # Ação: Gera instâncias
        instances = HabitInstanceService.generate_instances(everyday_habit.id, start, end)

        # Verificação: Deve criar 7 instâncias (uma por dia)
        assert len(instances) == 7

        # Verificação: Cada instância tem data correta
        expected_dates = [start + timedelta(days=i) for i in range(7)]
        actual_dates = [inst.date for inst in instances]
        assert actual_dates == expected_dates

        # Verificação: Todas têm horários corretos
        for inst in instances:
            assert inst.scheduled_start == time(7, 0)
            assert inst.scheduled_end == time(8, 0)
            assert inst.status == Status.PENDING

    def test_generate_weekdays_only(self, weekdays_habit):
        """Gera instâncias para hábito WEEKDAYS - pula fins de semana.

        DADO: Hábito com recorrência WEEKDAYS
        QUANDO: Gerar instâncias para semana completa (Seg-Dom)
        ENTÃO: Deve criar apenas 5 instâncias (Seg-Sex)

        Regra de Negócio: WEEKDAYS exclui sábado e domingo.
        Caso Extremo: Semana contendo dias de fim de semana.
        """
        # Preparação: Encontra próxima segunda-feira
        today = date.today()
        days_until_monday = (7 - today.weekday()) % 7
        monday = today + timedelta(days=days_until_monday)
        sunday = monday + timedelta(days=6)

        # Ação: Gera para semana completa
        instances = HabitInstanceService.generate_instances(weekdays_habit.id, monday, sunday)

        # Verificação: Apenas 5 instâncias (Seg-Sex)
        assert len(instances) == 5

        # Verificação: Sem sábado ou domingo
        for inst in instances:
            weekday = inst.date.weekday()
            assert weekday < 5, f"Instância no fim de semana: {inst.date}"

    def test_generate_habit_not_found(self):
        """Gerar instâncias para hábito inexistente levanta erro.

        DADO: ID de hábito inexistente
        QUANDO: Tentar gerar instâncias
        ENTÃO: Deve levantar ValueError

        Caso Extremo: habit_id inválido.
        """
        with pytest.raises(ValueError, match="Habit 99999 not found"):
            HabitInstanceService.generate_instances(
                99999, date.today(), date.today() + timedelta(days=7)
            )

    def test_generate_single_day(self, everyday_habit):
        """Gera instâncias para período de um único dia.

        DADO: Hábito com recorrência EVERYDAY
        QUANDO: Gerar para start_date == end_date
        ENTÃO: Deve criar exatamente 1 instância

        Caso Extremo: Período mínimo (um dia).
        """
        # Preparação: Mesma data para início e fim
        target_date = date.today()

        # Ação: Gera para dia único
        instances = HabitInstanceService.generate_instances(
            everyday_habit.id, target_date, target_date
        )

        # Verificação: Exatamente uma instância
        assert len(instances) == 1
        assert instances[0].date == target_date


class TestMarkCompleted:
    """Testa método mark_completed() - GAP DE COBERTURA."""

    def test_mark_completed_success(self, test_engine, everyday_habit):
        """Marca instância como completada com sucesso.

        DADO: HabitInstance com status PLANNED
        QUANDO: Marcar como completa
        ENTÃO: Status muda para COMPLETED

        Regra de Negócio: Usuários podem marcar hábitos como feitos.
        """
        # Preparação: Cria instância
        instances = HabitInstanceService.generate_instances(
            everyday_habit.id, date.today(), date.today()
        )
        instance_id = instances[0].id

        # Ação: Marca como completa
        updated = HabitInstanceService.mark_completed(instance_id)

        # Verificação: Status atualizado
        assert updated is not None
        assert updated.status == Status.DONE

    def test_mark_completed_nonexistent(self):
        """Marcar instância inexistente retorna None.

        DADO: ID de instância inexistente
        QUANDO: Tentar marcar como completa
        ENTÃO: Deve retornar None (não levanta erro)

        Caso Extremo: instance_id inválido.
        Regra de Negócio: Falha graciosa para instâncias ausentes.
        """
        # Ação: Tenta marcar inexistente
        result = HabitInstanceService.mark_completed(99999)

        # Verificação: Retorna None
        assert result is None


class TestMarkSkipped:
    """Testa método mark_skipped() - GAP DE COBERTURA."""

    def test_mark_skipped_success(self, test_engine, everyday_habit):
        """Marca instância como pulada com sucesso.

        DADO: HabitInstance com status PLANNED
        QUANDO: Marcar como pulada
        ENTÃO: Status muda para SKIPPED

        Regra de Negócio: Usuários podem pular hábitos intencionalmente.
        Caso de Uso: Usuário decide não fazer hábito hoje.
        """
        # Preparação: Cria instância
        instances = HabitInstanceService.generate_instances(
            everyday_habit.id, date.today(), date.today()
        )
        instance_id = instances[0].id

        # Ação: Marca como pulada
        updated = HabitInstanceService.mark_skipped(instance_id)

        # Verificação: Status atualizado
        assert updated is not None
        assert updated.status == Status.NOT_DONE

    def test_mark_skipped_nonexistent(self):
        """Marcar instância inexistente retorna None.

        DADO: ID de instância inexistente
        QUANDO: Tentar marcar como pulada
        ENTÃO: Deve retornar None (não levanta erro)

        Caso Extremo: instance_id inválido.
        """
        # Ação: Tenta marcar inexistente
        result = HabitInstanceService.mark_skipped(99999)

        # Verificação: Retorna None
        assert result is None
