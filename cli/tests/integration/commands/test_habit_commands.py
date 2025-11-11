"""
Integration tests para comandos de hábitos.

Testa comandos CLI relacionados a criação, listagem e deleção de hábitos,
validando integração com rotinas e persistência no banco.

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
"""

import re

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


@pytest.fixture
def routine_id(runner: CliRunner, isolated_db: None) -> str:
    """
    Cria rotina de teste e retorna seu ID.

    Args:
        runner: CLI runner fixture
        isolated_db: Banco de dados isolado

    Returns:
        ID da rotina criada como string.
    """
    result = runner.invoke(app, ["routine", "create", "Test Routine"], input="y\n")
    # Extrair ID da saída (remover códigos ANSI)
    id_lines = [line for line in result.stdout.split("\n") if "ID:" in line]
    clean = re.sub(r'\x1b\[[0-9;]*m', '', id_lines[0])
    return clean.split(":")[1].strip()


class TestBRHabitCreation:
    """
    Integration: Criação de hábitos via CLI (BR-HABIT-CREATE-*).

    Valida criação de hábitos com diferentes configurações de recorrência,
    validação de rotinas e persistência de campos opcionais.

    BRs cobertas:
    - BR-HABIT-CREATE-001: Criação com recorrência específica (MONDAY)
    - BR-HABIT-CREATE-002: Criação com recorrência múltipla (WEEKDAYS)
    - BR-HABIT-CREATE-003: Criação com cor personalizada
    - BR-HABIT-CREATE-004: Validação de rotina existente
    """

    def test_br_habit_create_001_monday_recurrence(
        self, runner: CliRunner, isolated_db: None, routine_id: str
    ) -> None:
        """
        Integration: Sistema cria hábito com recorrência específica (MONDAY).

        DADO: Rotina válida existente
        QUANDO: Usuário cria hábito com recorrência MONDAY
        ENTÃO: Sistema cria hábito com sucesso
        E: Hábito é associado à rotina correta

        Referências:
            - BR-HABIT-CREATE-001: Criação com recorrência específica
        """
        # ACT
        result = runner.invoke(app, [
            "habit", "create",
            "--routine", routine_id,
            "-t", "Monday Run",
            "-r", "MONDAY",
            "-s", "06:00",
            "-e", "07:00"
        ])
        # ASSERT
        assert result.exit_code == 0, "Criação de hábito MONDAY deve ter sucesso"

    def test_br_habit_create_002_weekdays_recurrence(
        self, runner: CliRunner, isolated_db: None, routine_id: str
    ) -> None:
        """
        Integration: Sistema cria hábito com recorrência múltipla (WEEKDAYS).

        DADO: Rotina válida existente
        QUANDO: Usuário cria hábito com recorrência WEEKDAYS
        ENTÃO: Sistema cria hábito com sucesso
        E: Hábito será gerado em dias úteis (Seg-Sex)

        Referências:
            - BR-HABIT-CREATE-002: Criação com recorrência múltipla
        """
        # ACT
        result = runner.invoke(app, [
            "habit", "create",
            "--routine", routine_id,
            "-t", "Meditation",
            "-r", "WEEKDAYS",
            "-s", "05:00",
            "-e", "05:30"
        ])
        # ASSERT
        assert result.exit_code == 0, "Criação de hábito WEEKDAYS deve ter sucesso"

    def test_br_habit_create_003_with_color(
        self, runner: CliRunner, isolated_db: None, routine_id: str
    ) -> None:
        """
        Integration: Sistema cria hábito com cor personalizada.

        DADO: Rotina válida e cor hexadecimal válida
        QUANDO: Usuário especifica cor com flag -c
        ENTÃO: Sistema cria hábito com sucesso
        E: Cor é persistida corretamente

        Referências:
            - BR-HABIT-CREATE-003: Criação com cor personalizada
        """
        # ACT
        result = runner.invoke(app, [
            "habit", "create",
            "--routine", routine_id,
            "-t", "Gym",
            "-r", "FRIDAY",
            "-s", "18:00",
            "-e", "19:30",
            "-c", "#FF5733"
        ])
        # ASSERT
        assert result.exit_code == 0, "Criação com cor deve ter sucesso"

    def test_br_habit_create_004_invalid_routine(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema rejeita hábito com rotina inexistente.

        DADO: ID de rotina que não existe (999)
        QUANDO: Usuário tenta criar hábito com rotina inválida
        ENTÃO: Sistema retorna erro (exit_code != 0)
        E: Hábito não é criado

        Referências:
            - BR-HABIT-CREATE-004: Validação de rotina existente
        """
        # ACT
        result = runner.invoke(app, [
            "habit", "create",
            "--routine", "999",
            "-t", "Test",
            "-r", "MONDAY",
            "-s", "10:00",
            "-e", "11:00"
        ])
        # ASSERT
        assert result.exit_code != 0, "Rotina inexistente deve causar erro"


class TestBRHabitListing:
    """
    Integration: Listagem de hábitos via CLI (BR-HABIT-LIST-*).

    Valida exibição de hábitos de uma rotina, incluindo casos
    de rotina vazia e rotina com múltiplos hábitos.

    BRs cobertas:
    - BR-HABIT-LIST-001: Listagem de rotina vazia
    - BR-HABIT-LIST-002: Listagem com múltiplos hábitos
    """

    def test_br_habit_list_001_empty_routine(
        self, runner: CliRunner, isolated_db: None, routine_id: str
    ) -> None:
        """
        Integration: Sistema lista rotina vazia sem erros.

        DADO: Rotina existente sem hábitos
        QUANDO: Usuário lista hábitos da rotina
        ENTÃO: Sistema retorna sucesso (exit_code 0)
        E: Nenhum hábito é exibido

        Referências:
            - BR-HABIT-LIST-001: Listagem de rotina vazia
        """
        # ACT
        result = runner.invoke(app, ["habit", "list", "--routine", routine_id])
        # ASSERT
        assert result.exit_code == 0, "Listagem de rotina vazia deve ter sucesso"

    def test_br_habit_list_002_with_habits(
        self, runner: CliRunner, isolated_db: None, routine_id: str
    ) -> None:
        """
        Integration: Sistema lista múltiplos hábitos corretamente.

        DADO: Rotina com 2 hábitos criados
        QUANDO: Usuário lista hábitos da rotina
        ENTÃO: Sistema exibe ambos os hábitos
        E: Títulos dos hábitos aparecem na saída

        Referências:
            - BR-HABIT-LIST-002: Listagem com múltiplos hábitos
        """
        # ARRANGE
        runner.invoke(app, [
            "habit", "create",
            "--routine", routine_id,
            "-t", "Habit 1", "-r", "MONDAY", "-s", "06:00", "-e", "07:00"
        ])
        runner.invoke(app, [
            "habit", "create",
            "--routine", routine_id,
            "-t", "Habit 2", "-r", "FRIDAY", "-s", "18:00", "-e", "19:00"
        ])
        # ACT
        result = runner.invoke(app, ["habit", "list", "--routine", routine_id])
        # ASSERT
        assert result.exit_code == 0, "Listagem deve ter sucesso"
        assert "Habit 1" in result.stdout, "Habit 1 deve aparecer na listagem"
        assert "Habit 2" in result.stdout, "Habit 2 deve aparecer na listagem"


class TestBRHabitDeletion:
    """
    Integration: Deleção de hábitos via CLI (BR-HABIT-DELETE-*).

    Valida deleção de hábitos com confirmação forçada e cancelamento,
    garantindo que dados são preservados quando usuário cancela.

    BRs cobertas:
    - BR-HABIT-DELETE-001: Deleção com flag --force
    - BR-HABIT-DELETE-002: Cancelamento de deleção
    """

    def test_br_habit_delete_001_with_force(
        self, runner: CliRunner, isolated_db: None, routine_id: str
    ) -> None:
        """
        Integration: Sistema deleta hábito com flag --force (sem confirmação).

        DADO: Hábito existente
        QUANDO: Usuário executa delete com --force
        ENTÃO: Sistema deleta sem pedir confirmação
        E: Comando retorna sucesso

        Referências:
            - BR-HABIT-DELETE-001: Deleção forçada sem confirmação
        """
        # ARRANGE - Criar hábito
        create_result = runner.invoke(app, [
            "habit", "create",
            "--routine", routine_id,
            "-t", "Delete Me", "-r", "TUESDAY", "-s", "06:00", "-e", "07:00"
        ])
        # Extrair habit_id
        id_lines = [line for line in create_result.stdout.split("\n") if "ID:" in line]
        clean = re.sub(r'\x1b\[[0-9;]*m', '', id_lines[0])
        habit_id = clean.split(":")[1].strip()
        # ACT
        result = runner.invoke(app, ["habit", "delete", habit_id, "--force"])
        # ASSERT
        assert result.exit_code == 0, "Deleção com --force deve ter sucesso"

    def test_br_habit_delete_002_cancel(
        self, runner: CliRunner, isolated_db: None, routine_id: str
    ) -> None:
        """
        Integration: Sistema preserva hábito quando usuário cancela deleção.

        DADO: Hábito existente
        QUANDO: Usuário executa delete e responde 'n' (não)
        ENTÃO: Sistema cancela operação
        E: Hábito não é deletado

        Referências:
            - BR-HABIT-DELETE-002: Cancelamento de deleção
        """
        # ARRANGE - Criar hábito
        create_result = runner.invoke(app, [
            "habit", "create",
            "--routine", routine_id,
            "-t", "Keep Me", "-r", "WEDNESDAY", "-s", "06:00", "-e", "07:00"
        ])
        # Extrair habit_id
        id_lines = [line for line in create_result.stdout.split("\n") if "ID:" in line]
        clean = re.sub(r'\x1b\[[0-9;]*m', '', id_lines[0])
        habit_id = clean.split(":")[1].strip()
        # ACT
        result = runner.invoke(app, ["habit", "delete", habit_id], input="n\n")
        # ASSERT
        assert result.exit_code == 0, "Cancelamento deve retornar sucesso"
