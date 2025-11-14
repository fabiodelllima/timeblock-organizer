"""
E2E tests validando workflow completo de criação de eventos.

Este arquivo testa o fluxo end-to-end: Rotina → Hábito → Instâncias → Visualização

Referências:
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
    """
    Cria banco de dados temporário isolado para E2E tests.

    Returns:
        Path para banco de dados temporário.
    """
    db_path = tmp_path / "test.db"
    return db_path


class TestBREventCreationWorkflow:
    """
    E2E: Workflow completo de criação de eventos.

    Valida fluxo: Rotina → Hábito → Instâncias → Visualização

    BRs cobertas:
    - BR-ROUTINE-001: Criação de rotinas
    - BR-HABIT-001: Criação de hábitos em rotinas
    - BR-EVENT-001: Instâncias agendadas corretamente
    """

    def test_br_routine_habit_schedule_complete_flow(
        self, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Usuário cria rotina completa com múltiplos hábitos.

        DADO: Sistema inicializado
        QUANDO: Usuário cria rotina "Manhã Produtiva"
        E: Adiciona 3 hábitos (Meditação, Exercício, Café)
        E: Gera instâncias para 1 semana
        ENTÃO: Sistema cria todos eventos corretamente
        E: Lista mostra instâncias esperadas
        E: Horários não conflitam

        Referências:
            - BR-ROUTINE-001: Uma rotina pode ter múltiplos hábitos
            - BR-HABIT-001: Hábitos pertencem a rotinas
            - BR-EVENT-001: Instâncias seguem schedule do hábito
        """
        # Configurar banco de dados isolado via variável de ambiente
        monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))

        runner = CliRunner()

        # 1. Init sistema
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0, f"Sistema deve inicializar com sucesso. Output: {result.output}"

        # 2. Criar rotina
        result = runner.invoke(app, [
            "routine", "create", "Manhã Produtiva"
        ])
        assert result.exit_code == 0, f"Criação de rotina deve ter sucesso. Output: {result.output}"
        assert "criada" in result.output.lower() or "created" in result.output.lower(), (
            "Feedback de criação deve aparecer"
        )

        # 3. Adicionar 3 hábitos com horários não conflitantes
        habits = [
            ("Meditação", "06:00", "06:20", "EVERYDAY"),
            ("Exercício", "06:30", "07:30", "WEEKDAYS"),
            ("Café da Manhã", "08:00", "08:30", "EVERYDAY"),
        ]

        for title, start, end, repeat in habits:
            result = runner.invoke(app, [
                "habit", "create",
                "--title", title,
                "--start", start,
                "--end", end,
                "--repeat", repeat
            ])
            assert result.exit_code == 0, (
                f"Criação de hábito '{title}' deve ter sucesso. Output: {result.output}"
            )
            assert (
                "criado" in result.output.lower()
                or "created" in result.output.lower()
            ), f"Feedback de criação para '{title}' deve aparecer"

        # 4. Gerar instâncias para 1 semana
        result = runner.invoke(app, [
            "schedule", "generate", "--days", "7"
        ])
        assert result.exit_code == 0, f"Geração deve ter sucesso. Output: {result.output}"
        # Meditação (7) + Exercício (5 weekdays) + Café (7) = 19 instâncias
        assert (
            "gerada" in result.output.lower()
            or "generated" in result.output.lower()
            or "19" in result.output
        ), "Deve indicar geração de instâncias"

        # 5. Listar agenda da semana
        result = runner.invoke(app, ["list", "week"])
        assert result.exit_code == 0, f"Listagem deve ter sucesso. Output: {result.output}"
        assert "Meditação" in result.output, "Hábito Meditação deve aparecer"
        assert "Exercício" in result.output, "Hábito Exercício deve aparecer"
        assert "Café da Manhã" in result.output, "Hábito Café da Manhã deve aparecer"

        # 6. Verificar ausência de conflitos
        assert (
            "conflito" not in result.output.lower()
        ), "Não deve haver conflitos em horários planejados corretamente"
        assert (
            "overlap" not in result.output.lower()
        ), "Não deve haver sobreposições"

    def test_br_event_creation_validates_time_ranges(
        self, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Sistema valida horários ao criar hábitos.

        DADO: Sistema inicializado com rotina
        QUANDO: Usuário tenta criar hábito com horário inválido
        ENTÃO: Sistema rejeita e informa erro de validação

        Referências:
            - BR-COMMON-001: Validação de formato de tempo
            - BR-COMMON-003: Validação de ranges válidos
        """
        # Configurar banco de dados isolado
        monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))

        runner = CliRunner()

        # Setup
        runner.invoke(app, ["init"])
        runner.invoke(app, ["routine", "create", "Test Routine"])

        # Tentar criar com horário inválido (25:00)
        result = runner.invoke(app, [
            "habit", "create",
            "--title", "Invalid Habit",
            "--start", "25:00",
            "--end", "26:00",
            "--repeat", "EVERYDAY"
        ])

        # Deve falhar com erro de validação
        assert result.exit_code != 0, "Criação com horário inválido deve falhar"
        assert (
            "inválido" in result.output.lower()
            or "invalid" in result.output.lower()
            or "erro" in result.output.lower()
            or "error" in result.output.lower()
        ), f"Deve informar erro de validação. Output: {result.output}"
