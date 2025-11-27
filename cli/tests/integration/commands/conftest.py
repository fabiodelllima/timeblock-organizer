"""Fixtures para testes de comandos CLI."""

import re
from contextlib import contextmanager
from unittest.mock import patch

import pytest
from sqlmodel import SQLModel, create_engine
from typer.testing import CliRunner

from src.timeblock.main import app


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


@pytest.fixture
def routine_id(runner: CliRunner, isolated_db: None) -> str:
    """
    Cria rotina de teste e retorna seu ID.

    ATENÇÃO: Esta fixture NÃO garante que a rotina está ativa.
    Para testes que precisam de rotina ativa, use `active_routine_id`.

    Args:
        runner: CLI runner fixture
        isolated_db: Banco de dados isolado

    Returns:
        ID da rotina criada como string.
    """
    result = runner.invoke(app, ["routine", "create", "Test Routine"], input="y\n")
    # Extrair ID da saída (remover códigos ANSI)
    id_lines = [line for line in result.stdout.split("\n") if "ID:" in line]
    clean = re.sub(r"\x1b\[[0-9;]*m", "", id_lines[0])
    return clean.split(":")[1].strip()


@pytest.fixture
def active_routine_id(runner: CliRunner, isolated_db: None) -> str:
    """
    Cria rotina de teste e GARANTE que está ativa.

    Valida:
        - BR-ROUTINE-001: Criar rotina não ativa automaticamente (requer activate())
        - BR-ROUTINE-004: Comandos habit precisam de rotina ativa

    Esta é a fixture RECOMENDADA para testes de comandos habit.

    Args:
        runner: CLI runner fixture
        isolated_db: Banco de dados isolado

    Returns:
        ID da rotina ativa como string.
    """
    # 1. Criar rotina (BR-ROUTINE-001: não ativa automaticamente)
    result = runner.invoke(app, ["routine", "create", "Test Routine"])
    assert result.exit_code == 0, f"Criação de rotina falhou: {result.output}"

    # 2. Extrair ID da saída (remover códigos ANSI)
    id_lines = [line for line in result.stdout.split("\n") if "ID:" in line]
    assert id_lines, f"ID não encontrado na saída: {result.output}"

    clean = re.sub(r"\x1b\[[0-9;]*m", "", id_lines[0])
    routine_id = clean.split(":")[1].strip()

    # 3. ATIVAR explicitamente (validando BR-ROUTINE-001: criar ≠ ativar)
    result = runner.invoke(app, ["routine", "activate", routine_id])
    assert result.exit_code == 0, f"Ativação de rotina falhou: {result.output}"

    return routine_id
