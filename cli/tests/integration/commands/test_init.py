"""
Integration tests para comando init.

Testa inicialização do banco de dados, incluindo criação inicial,
recriação com confirmação e tratamento de erros.

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix

TECHNICAL DEBT:
    Imports de 'app' dentro das funções são MÁ PRÁTICA necessária devido a
    acoplamento forte do código de produção com variáveis de ambiente globais.

    Problema: src/timeblock/database/engine.py lê TIMEBLOCK_DB_PATH no momento
    do import, tornando impossível testar com banco isolado se importarmos no topo.

    Solução ideal: Refatorar engine.py para usar Dependency Injection, permitindo
    injetar database path via parâmetros em vez de variáveis de ambiente globais.

    TODO(Sprint Futura): Desacoplar database engine de variáveis de ambiente
    Referência: PEP 8 - "Imports should usually be on separate lines at the top"
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from typer.testing import CliRunner


@pytest.fixture(autouse=True)
def isolated_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """
    Cria banco de dados isolado em diretório temporário.

    Args:
        tmp_path: Diretório temporário do pytest
        monkeypatch: Fixture para modificar variáveis de ambiente

    Yields:
        Path para arquivo de banco de dados isolado.

    Nota:
        Esta fixture usa autouse=True e força reimport de módulos
        para garantir isolamento completo entre testes.
    """
    db_file = tmp_path / "test.db"
    # Definir variável de ambiente ANTES de importar
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_file))
    # Forçar reimport para usar nova variável de ambiente
    import sys

    for module in [
        "src.timeblock.database",
        "src.timeblock.commands.init",
        "src.timeblock.main",
    ]:
        if module in sys.modules:
            del sys.modules[module]
    yield db_file


class TestBRSystemInitialization:
    """
    Integration: Inicialização do sistema (BR-SYSTEM-INIT-*).

    Valida criação, recriação e tratamento de erros do banco de dados
    durante inicialização do sistema.

    BRs cobertas:
    - BR-SYSTEM-INIT-001: Criação inicial do banco
    - BR-SYSTEM-INIT-002: Recriação com confirmação do usuário
    - BR-SYSTEM-INIT-003: Cancelamento de recriação
    - BR-SYSTEM-INIT-004: Tratamento de erros de criação
    """

    def test_br_system_init_001_creates_database(self, isolated_db: Path) -> None:
        """
        Integration: Sistema cria banco de dados quando não existe.

        DADO: Banco de dados não existe
        QUANDO: Usuário executa comando init
        ENTÃO: Sistema cria arquivo de banco com sucesso
        E: Mensagem de inicialização é exibida
        E: Arquivo do banco existe no filesystem

        Referências:
            - BR-SYSTEM-INIT-001: Criação inicial do banco
        """
        # TECHNICAL DEBT: Import aqui devido a global state em engine.py
        # Ver docstring do módulo para detalhes sobre o problema arquitetural
        from src.timeblock.main import app

        runner = CliRunner()
        # ACT
        result = runner.invoke(app, ["init"])
        # ASSERT
        assert result.exit_code == 0, "Inicialização deve ter sucesso"
        assert "initialized" in result.output.lower(), "Mensagem deve confirmar inicialização"
        assert isolated_db.exists(), "Arquivo do banco deve existir"

    def test_br_system_init_002_recreate_with_confirmation(self, isolated_db: Path) -> None:
        """
        Integration: Sistema recria banco quando usuário confirma.

        DADO: Banco de dados já existe
        QUANDO: Usuário executa init e responde 'y' (sim)
        ENTÃO: Sistema recria banco com sucesso
        E: Mensagem de inicialização é exibida

        Referências:
            - BR-SYSTEM-INIT-002: Recriação com confirmação

        Nota:
            Recriação apaga todos os dados existentes.
            Sistema deve pedir confirmação explícita.
        """
        # TECHNICAL DEBT: Import aqui devido a global state em engine.py
        from src.timeblock.main import app

        runner = CliRunner()
        # ARRANGE - Primeira inicialização
        runner.invoke(app, ["init"])
        # ACT - Segunda inicialização com confirmação
        result = runner.invoke(app, ["init"], input="y\n")
        # ASSERT
        assert result.exit_code == 0, "Recriação deve ter sucesso"
        assert "initialized" in result.output.lower(), "Mensagem deve confirmar reinicialização"

    def test_br_system_init_003_cancel_recreation(self, isolated_db: Path) -> None:
        """
        Integration: Sistema cancela recriação quando usuário recusa.

        DADO: Banco de dados já existe
        QUANDO: Usuário executa init e responde 'n' (não)
        ENTÃO: Sistema cancela operação
        E: Banco existente é preservado
        E: Mensagem de cancelamento é exibida

        Referências:
            - BR-SYSTEM-INIT-003: Cancelamento de recriação
        """
        # TECHNICAL DEBT: Import aqui devido a global state em engine.py
        from src.timeblock.main import app

        runner = CliRunner()
        # ARRANGE - Primeira inicialização
        runner.invoke(app, ["init"])
        # ACT - Segunda inicialização com cancelamento
        result = runner.invoke(app, ["init"], input="n\n")
        # ASSERT
        assert result.exit_code == 0, "Cancelamento deve retornar sucesso"
        assert "cancelled" in result.output.lower() or "aborted" in result.output.lower(), (
            "Mensagem deve indicar cancelamento"
        )

    def test_br_system_init_004_handles_database_error(
        self, isolated_db: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        Integration: Sistema trata erros de criação graciosamente.

        DADO: Função create_db_and_tables lança exceção
        QUANDO: Usuário executa comando init
        ENTÃO: Sistema retorna exit_code 1 (erro)
        E: Mensagem de erro é exibida
        E: Sistema não trava (exceção tratada)

        Referências:
            - BR-SYSTEM-INIT-004: Tratamento de erros de criação
        """
        # TECHNICAL DEBT: Import aqui devido a global state em engine.py
        from src.timeblock.main import app

        runner = CliRunner()

        # ARRANGE - Mock para simular erro
        def mock_create_error() -> None:
            raise Exception("Simulated database error")

        monkeypatch.setattr("src.timeblock.commands.init.create_db_and_tables", mock_create_error)
        # ACT
        result = runner.invoke(app, ["init"])
        # ASSERT
        assert result.exit_code == 1, "Erro deve retornar exit_code 1"
        assert "error" in result.output.lower(), "Mensagem deve indicar erro"
