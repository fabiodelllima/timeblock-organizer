"""
Integration tests para comando list.

Testa listagem de eventos/tasks via CLI, validando exibição
correta de dados e comportamento com banco vazio.

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
"""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from typer.testing import CliRunner

from src.timeblock.main import app
from src.timeblock.models import Event, EventStatus


@pytest.fixture(scope="function")
def isolated_db(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """
    Cria banco de dados isolado em memória para cada teste.

    Args:
        monkeypatch: Fixture para modificar funções

    Yields:
        None (engine é mockado via monkeypatch)

    Nota:
        Usa SQLite in-memory com StaticPool para permitir
        múltiplas conexões no mesmo banco durante teste.
    """
    # Criar engine in-memory
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Context manager que retorna test engine
    @contextmanager
    def mock_engine_context():
        try:
            yield engine
        finally:
            pass  # Não dispose durante teste

    # Mock get_engine_context para retornar test engine
    monkeypatch.setattr("src.timeblock.database.get_engine_context", mock_engine_context)
    monkeypatch.setattr("src.timeblock.commands.list.get_engine_context", mock_engine_context)

    # Criar tabelas
    SQLModel.metadata.create_all(engine)

    yield

    # Cleanup
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


class TestBREventListing:
    """
    Integration: Listagem de eventos via CLI (BR-EVENT-LIST-*).

    Valida exibição de eventos criados, comportamento com banco vazio
    e execução sem erros do comando list.

    BRs cobertas:
    - BR-EVENT-LIST-001: Comando executa sem erros
    - BR-EVENT-LIST-002: Exibe eventos criados
    - BR-EVENT-LIST-003: Funciona com banco vazio
    """

    def test_br_event_list_001_command_executes(self, isolated_db: None) -> None:
        """
        Integration: Comando list executa sem erros.

        DADO: Sistema inicializado
        QUANDO: Usuário executa comando list
        ENTÃO: Comando retorna exit_code 0
        E: Nenhum erro é lançado

        Referências:
            - BR-EVENT-LIST-001: Comando executa sem erros
        """
        # ACT
        runner = CliRunner()
        result = runner.invoke(app, ["list"])
        # ASSERT
        assert result.exit_code == 0, "List deve executar sem erros"

    def test_br_event_list_002_shows_created_events(
        self, isolated_db: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        Integration: Sistema exibe eventos criados na listagem.

        DADO: Dois eventos criados no banco (Morning Meeting, Lunch Break)
        QUANDO: Usuário executa comando list
        ENTÃO: Ambos os eventos aparecem na saída
        E: Títulos dos eventos são exibidos corretamente

        Referências:
            - BR-EVENT-LIST-002: Exibe eventos criados
        """
        # ARRANGE - Buscar engine mockado
        from src.timeblock.database import get_engine_context

        with get_engine_context() as engine:
            # Criar eventos de teste
            now = datetime.now(UTC)
            events = [
                Event(
                    title="Morning Meeting",
                    scheduled_start=now + timedelta(days=1),
                    scheduled_end=now + timedelta(days=1, hours=1),
                    status=EventStatus.PENDING,
                ),
                Event(
                    title="Lunch Break",
                    scheduled_start=now + timedelta(days=1, hours=5),
                    scheduled_end=now + timedelta(days=1, hours=6),
                    status=EventStatus.PENDING,
                ),
            ]
            with Session(engine) as session:
                for event in events:
                    session.add(event)
                session.commit()
        # ACT
        runner = CliRunner()
        result = runner.invoke(app, ["list"])
        # ASSERT
        assert result.exit_code == 0, "List deve executar com sucesso"
        assert "Morning Meeting" in result.output, "Evento 1 deve aparecer"
        assert "Lunch Break" in result.output, "Evento 2 deve aparecer"

    def test_br_event_list_003_empty_database(self, isolated_db: None) -> None:
        """
        Integration: Sistema lida graciosamente com banco vazio.

        DADO: Banco de dados sem eventos
        QUANDO: Usuário executa comando list
        ENTÃO: Comando retorna exit_code 0
        E: Nenhum erro é lançado (comportamento gracioso)

        Referências:
            - BR-EVENT-LIST-003: Funciona com banco vazio

        Nota:
            Sistema deve lidar com ausência de dados sem travar.
        """
        # ACT
        runner = CliRunner()
        result = runner.invoke(app, ["list"])
        # ASSERT
        assert result.exit_code == 0, "List em banco vazio deve ter sucesso"
