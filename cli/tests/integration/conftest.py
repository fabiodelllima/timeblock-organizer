"""Fixtures para testes de integração."""
import pytest
from sqlalchemy.orm import Session
from sqlmodel import SQLModel, create_engine

# Importar todos os modelos para SQLModel.metadata


@pytest.fixture(scope="function")
def integration_engine():
    """Engine de DB em memória para testes de integração."""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, echo=False
    )
    # Criar todas as tabelas
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def integration_session(integration_engine):
    """Sessão de DB para testes de integração."""
    with Session(integration_engine) as session:
        yield session
