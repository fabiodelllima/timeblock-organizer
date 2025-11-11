"""
Integration tests para comandos principais do CLI.

Testa comandos de nível raiz da aplicação, como version
e outros comandos utilitários do CLI principal.

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
"""

from typer.testing import CliRunner

from src.timeblock.main import app


class TestBRCLIMainCommands:
    """
    Integration: Comandos principais do CLI (BR-CLI-MAIN-*).

    Valida comandos de nível raiz que fornecem informações
    sobre a aplicação ou funcionalidades utilitárias.

    BRs cobertas:
    - BR-CLI-MAIN-001: Comando version exibe versão
    """

    def test_br_cli_main_001_version_command(self) -> None:
        """
        Integration: Comando version exibe informações de versão.

        DADO: Aplicação TimeBlock instalada
        QUANDO: Usuário executa comando version
        ENTÃO: Sistema exibe identificação "TimeBlock v"
        E: Sistema exibe número de versão atual (0.1.0)
        E: Comando retorna exit_code 0

        Referências:
            - BR-CLI-MAIN-001: Comando version

        Nota:
            Versão hardcoded no teste deve ser atualizada
            quando versão da aplicação mudar.
        """
        # ACT
        runner = CliRunner()
        result = runner.invoke(app, ["version"])
        # ASSERT
        assert result.exit_code == 0, "Comando version deve ter sucesso"
        assert "TimeBlock v" in result.output, "Deve exibir identificação"
        assert "0.1.0" in result.output, "Deve exibir número de versão"
