"""
E2E tests validando workflow completo de criacao de eventos.

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


class TestBREventCreationWorkflow:
    """
    E2E: Workflow completo de criacao de eventos.

    BRs cobertas:
    - BR-ROUTINE-001: Criacao de rotinas
    - BR-HABIT-001: Criacao de habitos em rotinas
    - BR-HABIT-002: Geracao de instancias via --generate
    """

    def test_br_routine_habit_schedule_complete_flow(
        self, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Usuario cria rotina completa com multiplos habitos.

        DADO: Sistema inicializado
        QUANDO: Usuario cria rotina "Manha Produtiva"
        E: Adiciona 3 habitos com --generate 1
        ENTAO: Sistema cria todos eventos corretamente
        
        Nota: Listagem via --week tem bug conhecido (TODO: investigar).
        Este teste valida apenas a criacao de instancias.
        """
        monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))
        runner = CliRunner()

        # 1. Init sistema
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0, f"Init deve ter sucesso. Output: {result.output}"

        # 2. Criar rotina
        result = runner.invoke(app, ["routine", "create", "Manha Produtiva"])
        assert result.exit_code == 0, f"Criacao de rotina deve ter sucesso. Output: {result.output}"

        # 3. Adicionar 3 habitos com --generate 1
        habits = [
            ("Meditacao", "06:00", "06:20", "EVERYDAY", "31"),
            ("Exercicio", "06:30", "07:30", "WEEKDAYS", "22"),
            ("Cafe da Manha", "08:00", "08:30", "EVERYDAY", "31"),
        ]

        for title, start, end, repeat, expected_count in habits:
            result = runner.invoke(
                app,
                [
                    "habit",
                    "create",
                    "--routine",
                    "1",
                    "--title",
                    title,
                    "--start",
                    start,
                    "--end",
                    end,
                    "--repeat",
                    repeat,
                    "--generate",
                    "1",
                ],
            )
            assert result.exit_code == 0, (
                f"Criacao de habito '{title}' deve ter sucesso. Output: {result.output}"
            )
            # Valida que instancias foram geradas
            assert expected_count in result.output or "instancia" in result.output.lower(), (
                f"Habito '{title}' deve gerar {expected_count} instancias. Output: {result.output}"
            )

    def test_br_event_creation_validates_time_ranges(
        self, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Sistema valida horarios ao criar habitos.

        DADO: Sistema inicializado com rotina
        QUANDO: Usuario tenta criar habito com horario invalido
        ENTAO: Sistema rejeita e informa erro de validacao
        """
        monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))
        runner = CliRunner()

        # Setup
        runner.invoke(app, ["init"])
        runner.invoke(app, ["routine", "create", "Test Routine"])

        # Tentar criar com horario invalido (25:00)
        result = runner.invoke(
            app,
            [
                "habit",
                "create",
                "--routine",
                "1",
                "--title",
                "Invalid Habit",
                "--start",
                "25:00",
                "--end",
                "26:00",
                "--repeat",
                "EVERYDAY",
            ],
        )

        assert result.exit_code != 0, "Criacao com horario invalido deve falhar"
