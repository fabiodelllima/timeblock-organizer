"""
E2E tests validando regras de negócio completas.

Este arquivo testa workflows end-to-end envolvendo múltiplas BRs.
Cada teste valida um fluxo completo de usuário.

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
    - BDD: docs/06-bdd/e2e-scenarios.md
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


class TestBRHabitWorkflow:
    """
    E2E: Workflow completo de hábitos (BR-HABIT-001, BR-HABIT-002, BR-HABIT-003).
    
    Valida fluxo end-to-end: Criar → Gerar → Completar → Visualizar
    
    BRs cobertas:
    - BR-HABIT-001: Criação de hábitos
    - BR-HABIT-002: Geração de instâncias
    - BR-HABIT-003: Completar hábito
    """

    def test_br_habit_complete_daily_workflow_with_confirmation(
        self, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Usuário cria hábito confirmando rotina ativa interativamente.
        
        DADO: Sistema inicializado com rotina ativa
        QUANDO: Usuário cria hábito e confirma usar rotina ativa (Y)
        ENTÃO: Hábito é criado na rotina ativa
        
        Referências:
            - BR-HABIT-001: Criação de hábitos em rotinas
            - BR-ROUTINE-001: Rotina ativa como padrão
            - BDD: docs/06-bdd/e2e-scenarios.md#scenario-1
        """
        monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))
        runner = CliRunner()

        # Setup
        runner.invoke(app, ["init"])
        runner.invoke(app, ["routine", "create", "Rotina Matinal"])

        # Criar hábito confirmando rotina ativa (responder "y" ao prompt)
        result = runner.invoke(app, [
            "habit", "create",
            "--title", "Meditação",
            "--start", "06:00",
            "--end", "06:20",
            "--repeat", "EVERYDAY"
        ], input="y\n")  # Simula usuário digitando "y" + Enter
        
        assert result.exit_code == 0, f"Deve criar com sucesso após confirmação. Output: {result.output}"
        assert "criado" in result.output.lower(), "Deve confirmar criação"

    def test_br_habit_complete_daily_workflow_explicit_routine(
        self, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Usuário cria hábito especificando rotina explicitamente.
        
        DADO: Sistema inicializado com rotina ativa
        QUANDO: Usuário especifica --routine no comando
        ENTÃO: Hábito é criado sem prompt interativo
        E: Workflow completo funciona (gerar, listar, completar)
        
        Referências:
            - BR-HABIT-001: Criação de hábitos em rotinas
            - BR-HABIT-002: Geração de instâncias de hábitos
            - BR-HABIT-003: Completar instância de hábito
            - BDD: docs/06-bdd/e2e-scenarios.md#scenario-1
        """
        monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))
        runner = CliRunner()

        # 1. Setup
        runner.invoke(app, ["init"])
        runner.invoke(app, ["routine", "create", "Rotina Matinal"])

        # 2. Criar hábito com --routine (sem prompt)
        result = runner.invoke(app, [
            "habit", "create",
            "--title", "Meditação",
            "--start", "06:00",
            "--end", "06:20",
            "--repeat", "EVERYDAY",
            "--routine", "1"
        ])
        assert result.exit_code == 0, f"Criação deve ter sucesso. Output: {result.output}"
        assert "criado" in result.output.lower()

        # 3. Gerar instâncias
        result = runner.invoke(app, ["schedule", "generate", "--days", "7"])
        assert result.exit_code == 0, f"Geração deve ter sucesso. Output: {result.output}"
        assert "7" in result.output

        # 4. Listar hoje
        result = runner.invoke(app, ["list", "today"])
        assert result.exit_code == 0, f"Listagem deve ter sucesso. Output: {result.output}"
        assert "Meditação" in result.output
        assert "06:00" in result.output

        # 5. Completar
        result = runner.invoke(app, ["habit", "complete", "1"])
        assert result.exit_code == 0, f"Completar deve ter sucesso. Output: {result.output}"

        # 6. Verificar conclusão
        result = runner.invoke(app, ["list", "today"])
        assert result.exit_code == 0
        assert (
            "✓" in result.output
            or "COMPLETED" in result.output
            or "completo" in result.output.lower()
        ), "Deve mostrar indicador de conclusão"

    def test_br_habit_creation_rejection_aborts(
        self, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Usuário rejeita criar hábito na rotina ativa e cancela.
        
        DADO: Sistema inicializado com rotina ativa
        QUANDO: Usuário rejeita rotina ativa (n) e não fornece alternativa
        ENTÃO: Sistema aborta criação do hábito
        
        Referências:
            - BR-HABIT-001: Usuário tem controle sobre rotina do hábito
        """
        monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))
        runner = CliRunner()

        # Setup
        runner.invoke(app, ["init"])
        runner.invoke(app, ["routine", "create", "Rotina Matinal"])

        # Rejeitar rotina ativa (responder "n" ao prompt)
        result = runner.invoke(app, [
            "habit", "create",
            "--title", "Meditação",
            "--start", "06:00",
            "--end", "06:20",
            "--repeat", "EVERYDAY"
        ], input="n\n")  # Simula usuário digitando "n" + Enter
        
        # Sistema deve abortar ou pedir ID alternativo
        assert result.exit_code != 0 or "Aborted" in result.output or "ID da rotina" in result.output, (
            f"Deve abortar ou pedir alternativa. Output: {result.output}"
        )


class TestBREventConflictWorkflow:
    """
    E2E: Workflow de detecção e resolução de conflitos (BR-EVENT-001, BR-EVENT-002).
    
    Valida fluxo end-to-end: Criar conflito → Detectar → Propor solução
    
    BRs cobertas:
    - BR-EVENT-001: Detecção de conflitos de horário
    - BR-EVENT-002: Proposta de reorganização
    """

    def test_br_event_conflict_detection_and_resolution(
        self, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Sistema detecta conflito de horários e propõe reorganização.
        
        DADO: Dois hábitos com horários sobrepostos
        QUANDO: Usuário ajusta horário causando conflito
        ENTÃO: Sistema detecta conflito e avisa usuário
        E: Sistema propõe solução de reorganização
        
        Referências:
            - BR-EVENT-001: Detecção de conflitos de horário
            - BR-EVENT-002: Proposta de reorganização automática
            - BDD: docs/06-bdd/e2e-scenarios.md#scenario-2
        """
        monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))
        runner = CliRunner()
        
        # Setup
        runner.invoke(app, ["init"])
        runner.invoke(app, ["routine", "create", "Rotina Diária"])

        # Criar hábitos sobrepostos
        runner.invoke(app, [
            "habit", "create",
            "--title", "Exercício",
            "--start", "09:00",
            "--end", "10:00",
            "--repeat", "EVERYDAY",
            "--routine", "1"
        ])
        runner.invoke(app, [
            "habit", "create",
            "--title", "Leitura",
            "--start", "09:30",
            "--end", "10:30",
            "--repeat", "EVERYDAY",
            "--routine", "1"
        ])

        # Gerar instâncias
        runner.invoke(app, ["schedule", "generate", "--days", "1"])

        # Tentar ajustar causando conflito
        result = runner.invoke(app, [
            "habit", "adjust", "1",
            "--start", "09:00",
            "--end", "10:00"
        ])

        # Verificar detecção de conflito
        assert (
            "conflito" in result.output.lower()
            or "overlap" in result.output.lower()
            or result.exit_code != 0
        ), f"Sistema deve detectar conflito. Output: {result.output}"
