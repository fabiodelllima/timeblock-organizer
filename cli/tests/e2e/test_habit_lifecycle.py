"""E2E tests validando regras de negócio completas."""


import pytest
from click.testing import CliRunner

from timeblock.main import app


@pytest.fixture
def isolated_db(tmp_path):
    """DB temporária isolada."""
    db_path = tmp_path / "test.db"
    # Mock DATABASE_PATH
    yield db_path

class TestHabitLifecycle:
    """Valida regra: Criar → Gerar → Completar → Visualizar."""

    def test_complete_daily_habit_workflow(self, isolated_db):
        """REGRA: Usuário consegue criar hábito diário e marcar completo."""
        runner = CliRunner()

        # REGRA: Sistema inicializa limpo
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        # REGRA: Usuário cria hábito recorrente
        result = runner.invoke(app, [
            "habit", "create", "Meditação",
            "--start", "06:00",
            "--duration", "20",
            "--recurrence", "EVERYDAY"
        ])
        assert result.exit_code == 0
        assert "criado" in result.output.lower()

        # REGRA: Sistema gera instâncias automaticamente
        result = runner.invoke(app, ["schedule", "generate", "--days", "7"])
        assert result.exit_code == 0
        assert "7" in result.output  # 7 instâncias

        # REGRA: Usuário vê hábito de hoje
        result = runner.invoke(app, ["list", "today"])
        assert result.exit_code == 0
        assert "Meditação" in result.output
        assert "06:00" in result.output

        # REGRA: Usuário marca como completo
        result = runner.invoke(app, ["habit", "complete", "1"])
        assert result.exit_code == 0

        # REGRA: Sistema mostra feedback visual de conclusão
        result = runner.invoke(app, ["list", "today"])
        assert result.exit_code == 0
        # Deve mostrar completado de alguma forma
        assert ("✓" in result.output or
                "COMPLETED" in result.output or
                "completo" in result.output.lower())

class TestEventReordering:
    """Valida regra: Conflitos são detectados e resolvidos."""

    def test_conflict_detection_and_resolution(self, isolated_db):
        """REGRA: Sistema detecta sobreposição e propõe reorganização."""
        runner = CliRunner()
        runner.invoke(app, ["init"])

        # REGRA: Criar dois hábitos no mesmo horário (conflito intencional)
        runner.invoke(app, [
            "habit", "create", "Exercício",
            "--start", "09:00", "--duration", "60"
        ])
        runner.invoke(app, [
            "habit", "create", "Leitura",
            "--start", "09:30", "--duration", "60"
        ])

        # REGRA: Gerar instâncias cria conflito
        runner.invoke(app, ["schedule", "generate", "--days", "1"])

        # REGRA: Sistema detecta conflito ao ajustar horário
        result = runner.invoke(app, [
            "habit", "adjust", "1", "--start", "09:00"
        ])

        # REGRA: Sistema avisa sobre conflito
        assert "conflito" in result.output.lower() or "overlap" in result.output.lower()

        # REGRA: Sistema propõe solução
        assert "proposta" in result.output.lower() or "reordering" in result.output.lower()
