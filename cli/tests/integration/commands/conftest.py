"""Fixtures para testes de comandos CLI."""

from contextlib import contextmanager
from unittest.mock import patch

import pytest
from sqlmodel import SQLModel, create_engine
from typer.testing import CliRunner


@pytest.fixture
def cli_runner():
    """Runner para comandos CLI."""
    return CliRunner()


@pytest.fixture
def mock_get_session(integration_session):
    """Mock do get_session para usar DB de teste em comandos CLI."""

    @contextmanager
    def _get_session():
        yield integration_session

    with patch("src.timeblock.database.engine.get_session", _get_session):
        yield


@pytest.fixture
def mock_get_engine_context(integration_engine):
    """Mock do get_engine_context para usar engine de teste."""

    @contextmanager
    def _get_engine():
        yield integration_engine

    with patch("src.timeblock.database.engine.get_engine_context", _get_engine):
        yield


@pytest.fixture
def cli_db_mocks(mock_get_session, mock_get_engine_context):
    """Agrupa todos os mocks de DB para CLI."""
    yield


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    """Cria DB isolado e configura DATABASE_PATH com tabelas inicializadas."""
    db_path = tmp_path / "test_cli.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))

    from src.timeblock import config

    monkeypatch.setattr(config, "DATABASE_PATH", db_path)

    # CRÍTICO: Criar as tabelas
    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)
    engine.dispose()

    return db_path
