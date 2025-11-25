"""
Integration tests for add command - error handling and validation.

Testa casos de erro e validação de entrada incorreta para garantir
que o sistema rejeita adequadamente dados inválidos.

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
"""

import pytest
from typer.testing import CliRunner

from src.timeblock.main import app


@pytest.fixture
def runner() -> CliRunner:
    """
    Cria CLI test runner.

    Returns:
        CliRunner configurado para testes.
    """
    return CliRunner()


class TestBRTaskValidationErrors:
    """
    Integration: Validação de erros na criação de tasks (BR-TASK-VALIDATION-*).

    Valida que o sistema rejeita adequadamente entradas inválidas
    e fornece mensagens de erro claras.

    BRs cobertas:
    - BR-TASK-VALIDATION-001: Rejeição de formato de hora inválido
    - BR-TASK-VALIDATION-002: Tratamento de início após fim (crossing midnight)
    - BR-TASK-VALIDATION-003: Validação de formato de cor hexadecimal
    - BR-TASK-VALIDATION-004: Validação de comprimento de cor
    """

    def test_br_task_validation_001_invalid_time_format(
        self, isolated_db: None, cli_runner: CliRunner
    ) -> None:
        """
        Integration: Sistema rejeita formato de hora inválido.

        DADO: Comando add com hora inválida (25:00)
        QUANDO: Usuário tenta criar evento
        ENTÃO: Sistema retorna exit_code 1 (erro)
        E: Mensagem de erro indica hora entre 0-23

        Referências:
            - BR-TASK-VALIDATION-001: Validação de formato de hora
        """
        # ACT
        result = cli_runner.invoke(
            app,
            ["add", "Meeting", "-s", "25:00", "-e", "10:00"],
        )

        # ASSERT
        assert result.exit_code == 1, "Hora inválida deve retornar erro"
        assert "Hour must be between 0 and 23" in result.output, (
            "Mensagem deve indicar range válido"
        )

    def test_br_task_validation_002_start_after_end_crossing_midnight(
        self, isolated_db: None, cli_runner: CliRunner
    ) -> None:
        """
        Integration: Sistema trata início após fim como crossing midnight (válido).

        DADO: Comando add com início 15:00 e fim 14:00
        QUANDO: Usuário cria evento (interpretado como cruzando meia-noite)
        ENTÃO: Sistema aceita como válido (exit_code 0)
        E: Mensagem informa que cruza meia-noite

        Referências:
            - BR-TASK-VALIDATION-002: Tratamento de crossing midnight

        Nota:
            Este é um caso especial onde início > fim é VÁLIDO,
            pois sistema assume intenção de cruzar meia-noite.
        """
        # ACT
        result = cli_runner.invoke(
            app,
            ["add", "Night Shift", "-s", "15:00", "-e", "14:00"],
        )

        # ASSERT
        assert result.exit_code == 0, "Crossing midnight deve ser aceito"
        assert "crosses midnight" in result.output.lower(), "Deve informar que cruza meia-noite"

    def test_br_task_validation_003_invalid_hex_color_format(
        self, isolated_db: None, cli_runner: CliRunner
    ) -> None:
        """
        Integration: Sistema rejeita cor sem prefixo # (hashtag).

        DADO: Comando add com cor sem # (3498db)
        QUANDO: Usuário tenta criar evento
        ENTÃO: Sistema retorna exit_code 1 (erro)
        E: Mensagem indica formato inválido

        Referências:
            - BR-TASK-VALIDATION-003: Validação de formato hexadecimal
        """
        # ACT
        result = cli_runner.invoke(
            app,
            ["add", "Meeting", "-s", "09:00", "-e", "10:00", "-c", "3498db"],
        )

        # ASSERT
        assert result.exit_code == 1, "Cor sem # deve retornar erro"
        assert "Invalid color format" in result.output, "Mensagem deve indicar formato inválido"

    def test_br_task_validation_004_invalid_hex_color_length(
        self, isolated_db: None, cli_runner: CliRunner
    ) -> None:
        """
        Integration: Sistema rejeita cor com comprimento incorreto.

        DADO: Comando add com cor curta (#123 em vez de #123456)
        QUANDO: Usuário tenta criar evento
        ENTÃO: Sistema retorna exit_code 1 (erro)
        E: Mensagem indica formato inválido

        Referências:
            - BR-TASK-VALIDATION-004: Validação de comprimento hexadecimal

        Nota:
            Formato válido: #RRGGBB (6 dígitos hexadecimais)
        """
        # ACT
        result = cli_runner.invoke(
            app,
            ["add", "Meeting", "-s", "09:00", "-e", "10:00", "-c", "#123"],
        )

        # ASSERT
        assert result.exit_code == 1, "Cor com comprimento errado deve retornar erro"
        assert "Invalid color format" in result.output, "Mensagem deve indicar formato inválido"
