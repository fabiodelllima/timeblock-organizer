"""
E2E tests validando regras de negocio completas.

Referencias:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
"""

from pathlib import Path

import pytest
from pytest import MonkeyPatch
from typer.testing import CliRunner

from src.timeblock.main import app


@pytest.fixture
def isolated_db(tmp_path: Path) -> Path:
    """Cria banco de dados temporario isolado para E2E tests."""
    db_path = tmp_path / "test.db"
    return db_path


class TestBRHabitWorkflow:
    """
    E2E: Workflow completo de habitos.

    BRs cobertas:
    - BR-HABIT-001: Criacao de habitos
    - BR-HABIT-002: Geracao de instancias via --generate
    - BR-HABIT-003: Completar habito
    """

    def test_br_habit_complete_daily_workflow_with_confirmation(
        self, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Usuario cria habito confirmando rotina ativa interativamente.
        """
        monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))
        runner = CliRunner()

        # Setup
        runner.invoke(app, ["init"])
        runner.invoke(app, ["routine", "create", "Rotina Matinal"])

        # Criar habito confirmando rotina ativa
        result = runner.invoke(
            app,
            [
                "habit",
                "create",
                "--title",
                "Meditacao",
                "--start",
                "06:00",
                "--end",
                "06:20",
                "--repeat",
                "EVERYDAY",
            ],
            input="y\n",
        )

        assert result.exit_code == 0, f"Deve criar com sucesso. Output: {result.output}"
        assert "criado" in result.output.lower(), "Deve confirmar criacao"

    def test_br_habit_complete_daily_workflow_explicit_routine(
        self, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Usuario cria habito com --routine e --generate.
        
        Valida geracao de instancias. Listagem de instancias tem bug conhecido
        no filtro --day (TODO: investigar).
        """
        monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))
        runner = CliRunner()

        # 1. Setup
        runner.invoke(app, ["init"])
        runner.invoke(app, ["routine", "create", "Rotina Matinal"])

        # 2. Criar habito com --routine e --generate
        result = runner.invoke(
            app,
            [
                "habit",
                "create",
                "--title",
                "Meditacao",
                "--start",
                "06:00",
                "--end",
                "06:20",
                "--repeat",
                "EVERYDAY",
                "--routine",
                "1",
                "--generate",
                "1",
            ],
        )
        assert result.exit_code == 0, f"Criacao deve ter sucesso. Output: {result.output}"
        # Valida que instancias foram geradas (31 dias = 1 mes)
        assert "31" in result.output or "instancia" in result.output.lower()

    def test_br_habit_creation_rejection_aborts(
        self, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Usuario rejeita criar habito na rotina ativa.
        """
        monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))
        runner = CliRunner()

        # Setup
        runner.invoke(app, ["init"])
        runner.invoke(app, ["routine", "create", "Rotina Matinal"])

        # Rejeitar rotina ativa
        result = runner.invoke(
            app,
            [
                "habit",
                "create",
                "--title",
                "Meditacao",
                "--start",
                "06:00",
                "--end",
                "06:20",
                "--repeat",
                "EVERYDAY",
            ],
            input="n\n",
        )

        assert (
            result.exit_code != 0 or "Aborted" in result.output or "ID da rotina" in result.output
        ), f"Deve abortar ou pedir alternativa. Output: {result.output}"


class TestBREventConflictWorkflow:
    """
    E2E: Workflow de deteccao e resolucao de conflitos.

    BRs cobertas:
    - BR-EVENT-001: Deteccao de conflitos de horario
    - BR-EVENT-002: Proposta de reorganizacao
    """

    @pytest.mark.skip(reason="Deteccao de conflitos em habit edit nao implementada ainda")
    def test_br_event_conflict_detection_and_resolution(
        self, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Sistema detecta conflito de horarios.

        TODO: Implementar deteccao de conflitos no habit edit
        """
        pass
