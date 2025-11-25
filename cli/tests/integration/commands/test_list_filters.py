"""
Integration tests para filtros do comando list.

Testa filtros temporais (mês, semana, dia), limite de resultados
e tratamento de erros no comando list.

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix

TECHNICAL DEBT:
    Imports de 'app' dentro das funções - mesma razão do test_init.py.
    Ver test_init.py docstring para explicação completa do problema arquitetural.
"""

from collections.abc import Iterator
from pathlib import Path
from typing import NoReturn

import pytest
from typer.testing import CliRunner


@pytest.fixture(autouse=True)
def isolated_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """
    Isola banco de dados em arquivo temporário.

    Args:
        tmp_path: Diretório temporário do pytest
        monkeypatch: Fixture para modificar env vars

    Yields:
        Path para arquivo de banco isolado.
    """
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))
    import sys

    for mod in [
        "src.timeblock.database",
        "src.timeblock.commands.list",
        "src.timeblock.main",
    ]:
        sys.modules.pop(mod, None)
    yield db_path


@pytest.fixture
def sample_events(isolated_db: Path) -> CliRunner:
    """
    Cria eventos de exemplo para testes de filtros.

    Args:
        isolated_db: Banco isolado

    Returns:
        CliRunner já inicializado com eventos de teste.
    """
    # TECHNICAL DEBT: Import aqui devido a global state
    from src.timeblock.main import app

    runner = CliRunner()
    # Inicializar banco
    runner.invoke(app, ["init"])
    # Adicionar evento de teste
    runner.invoke(app, ["add", "Event Today", "-s", "09:00", "-e", "10:00"])
    return runner


class TestBREventListFilters:
    """
    Integration: Filtros temporais para listagem (BR-EVENT-FILTER-*).

    Valida que filtros temporais (mês, semana, dia) funcionam corretamente
    e limitam resultados conforme especificado.

    BRs cobertas:
    - BR-EVENT-FILTER-001: Filtro por mês
    - BR-EVENT-FILTER-002: Filtro por semana
    - BR-EVENT-FILTER-003: Filtro por dia
    - BR-EVENT-FILTER-004: Limite de resultados
    - BR-EVENT-FILTER-005: Exibir todos os eventos
    - BR-EVENT-FILTER-006: Tratamento de erros de database
    """

    def test_br_event_filter_001_month_filter(self, sample_events: CliRunner) -> None:
        """
        Integration: Filtro por mês funciona corretamente.

        DADO: Eventos existentes no banco
        QUANDO: Usuário lista com --month 0 (mês atual)
        ENTÃO: Comando executa com sucesso
        E: Retorna apenas eventos do mês especificado

        Referências:
            - BR-EVENT-FILTER-001: Filtro por mês
        """
        # TECHNICAL DEBT: Import aqui devido a global state
        from src.timeblock.main import app

        # ACT
        result = sample_events.invoke(app, ["list", "--month", "0"])
        # ASSERT
        assert result.exit_code == 0, "Filtro por mês deve ter sucesso"

    def test_br_event_filter_002_week_filter(self, sample_events: CliRunner) -> None:
        """
        Integration: Filtro por semana funciona corretamente.

        DADO: Eventos existentes no banco
        QUANDO: Usuário lista com --week 0 (semana atual)
        ENTÃO: Comando executa com sucesso
        E: Retorna apenas eventos da semana especificada

        Referências:
            - BR-EVENT-FILTER-002: Filtro por semana
        """
        # TECHNICAL DEBT: Import aqui devido a global state
        from src.timeblock.main import app

        # ACT
        result = sample_events.invoke(app, ["list", "--week", "0"])
        # ASSERT
        assert result.exit_code == 0, "Filtro por semana deve ter sucesso"

    def test_br_event_filter_003_day_filter(self, sample_events: CliRunner) -> None:
        """
        Integration: Filtro por dia funciona corretamente.

        DADO: Eventos existentes no banco
        QUANDO: Usuário lista com --day 0 (hoje)
        ENTÃO: Comando executa com sucesso
        E: Retorna apenas eventos do dia especificado

        Referências:
            - BR-EVENT-FILTER-003: Filtro por dia
        """
        # TECHNICAL DEBT: Import aqui devido a global state
        from src.timeblock.main import app

        # ACT
        result = sample_events.invoke(app, ["list", "--day", "0"])
        # ASSERT
        assert result.exit_code == 0, "Filtro por dia deve ter sucesso"

    def test_br_event_filter_004_limit_results(self, sample_events: CliRunner) -> None:
        """
        Integration: Limite de resultados funciona corretamente.

        DADO: Eventos existentes no banco
        QUANDO: Usuário lista com --limit 5
        ENTÃO: Comando executa com sucesso
        E: Saída indica limitação a 5 eventos

        Referências:
            - BR-EVENT-FILTER-004: Limite de resultados
        """
        # TECHNICAL DEBT: Import aqui devido a global state
        from src.timeblock.main import app

        # ACT
        result = sample_events.invoke(app, ["list", "--limit", "5"])
        # ASSERT
        assert result.exit_code == 0, "Limite deve funcionar"
        assert "Latest 5 Events" in result.output or "5" in result.output, (
            "Saída deve indicar limite"
        )

    def test_br_event_filter_005_all_events(self, sample_events: CliRunner) -> None:
        """
        Integration: Flag --all exibe todos os eventos.

        DADO: Eventos existentes no banco
        QUANDO: Usuário lista com --all
        ENTÃO: Comando executa com sucesso
        E: Todos os eventos são exibidos (sem limite)

        Referências:
            - BR-EVENT-FILTER-005: Exibir todos os eventos
        """
        # TECHNICAL DEBT: Import aqui devido a global state
        from src.timeblock.main import app

        # ACT
        result = sample_events.invoke(app, ["list", "--all"])
        # ASSERT
        assert result.exit_code == 0, "List --all deve ter sucesso"

    def test_br_event_filter_006_handles_database_error(
        self, isolated_db: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        Integration: Sistema trata erros de database graciosamente.

        DADO: Função fetch_events_in_range lança exceção
        QUANDO: Usuário executa list
        ENTÃO: Comando retorna exit_code 1
        E: Mensagem de erro é exibida
        E: Sistema não trava

        Referências:
            - BR-EVENT-FILTER-006: Tratamento de erros

        Nota:
            Este teste remove duplicação do arquivo original
            onde o mesmo teste aparecia 3 vezes.
        """
        # TECHNICAL DEBT: Import aqui devido a global state
        from src.timeblock.main import app

        runner = CliRunner()
        runner.invoke(app, ["init"])

        # ARRANGE - Mock para simular erro
        def mock_fetch_error(*args: object, **kwargs: object) -> NoReturn:
            raise Exception("Database connection failed")

        monkeypatch.setattr("src.timeblock.commands.list.fetch_events_in_range", mock_fetch_error)
        # ACT
        result = runner.invoke(app, ["list"])
        # ASSERT
        assert result.exit_code == 1, "Erro de database deve retornar exit_code 1"
        assert "error" in result.output.lower(), "Mensagem deve indicar erro"
