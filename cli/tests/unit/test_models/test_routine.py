"""Testes para o modelo Routine."""
from datetime import datetime

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models.routine import Routine


@pytest.fixture
def engine():
    """Engine SQLite em memória."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Sessão de banco de dados."""
    with Session(engine) as session:
        yield session


def test_routine_creation(session):
    """Testa criação de rotina."""
    routine = Routine(name="Morning Routine")
    session.add(routine)
    session.commit()
    session.refresh(routine)
    assert routine.id is not None
    assert routine.name == "Morning Routine"
    assert routine.is_active is False  # BR-ROUTINE-001: Não ativa por padrão
    assert isinstance(routine.created_at, datetime)


def test_routine_defaults(session):
    """Testa valores padrão."""
    routine = Routine(name="Test")
    session.add(routine)
    session.commit()
    assert routine.is_active is False  # BR-ROUTINE-001: Default é False
    assert routine.created_at is not None


def test_routine_deactivation(session):
    """Testa desativação de rotina."""
    routine = Routine(name="Test", is_active=False)
    session.add(routine)
    session.commit()
    assert routine.is_active is False
