"""Testes de integração para comandos habit."""

import pytest
from typer.testing import CliRunner

from src.timeblock.main import app


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def routine_id(runner, isolated_db):
    """Cria rotina e retorna ID."""
    result = runner.invoke(app, ["routine", "create", "Test Routine"], input="y\n")
    import re
    id_line = [line for line in result.stdout.split("\n") if "ID:" in line][0]
    clean = re.sub(r'\x1b\[[0-9;]*m', '', id_line)
    return clean.split(":")[1].strip()


class TestHabitCreate:
    """Testes para habit create."""

    def test_create_monday(self, runner, isolated_db, routine_id):
        result = runner.invoke(app, [
            "habit", "create",
            "--routine", routine_id,
            "-t", "Monday Run",
            "-r", "MONDAY",
            "-s", "06:00",
            "-e", "07:00"
        ])

        assert result.exit_code == 0

    def test_create_weekdays(self, runner, isolated_db, routine_id):
        result = runner.invoke(app, [
            "habit", "create",
            "--routine", routine_id,
            "-t", "Meditation",
            "-r", "WEEKDAYS",
            "-s", "05:00",
            "-e", "05:30"
        ])

        assert result.exit_code == 0

    def test_create_with_color(self, runner, isolated_db, routine_id):
        result = runner.invoke(app, [
            "habit", "create",
            "--routine", routine_id,
            "-t", "Gym",
            "-r", "FRIDAY",
            "-s", "18:00",
            "-e", "19:30",
            "-c", "#FF5733"
        ])

        assert result.exit_code == 0

    def test_create_invalid_routine(self, runner, isolated_db):
        # Não usa routine_id fixture - banco vazio
        result = runner.invoke(app, [
            "habit", "create",
            "--routine", "999",
            "-t", "Test",
            "-r", "MONDAY",
            "-s", "10:00",
            "-e", "11:00"
        ])

        # Deve falhar porque rotina 999 não existe
        assert result.exit_code != 0


class TestHabitList:
    """Testes para habit list."""

    def test_list_empty(self, runner, isolated_db, routine_id):
        result = runner.invoke(app, ["habit", "list", "--routine", routine_id])

        assert result.exit_code == 0

    def test_list_with_habits(self, runner, isolated_db, routine_id):
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

        result = runner.invoke(app, ["habit", "list", "--routine", routine_id])

        assert result.exit_code == 0
        assert "Habit 1" in result.stdout
        assert "Habit 2" in result.stdout


class TestHabitDelete:
    """Testes para habit delete."""

    def test_delete_with_force(self, runner, isolated_db, routine_id):
        create_result = runner.invoke(app, [
            "habit", "create",
            "--routine", routine_id,
            "-t", "Delete Me", "-r", "TUESDAY", "-s", "06:00", "-e", "07:00"
        ])

        import re
        id_line = [line for line in create_result.stdout.split("\n") if "ID:" in line][0]
        clean = re.sub(r'\x1b\[[0-9;]*m', '', id_line)
        habit_id = clean.split(":")[1].strip()

        result = runner.invoke(app, ["habit", "delete", habit_id, "--force"])

        assert result.exit_code == 0

    def test_delete_cancel(self, runner, isolated_db, routine_id):
        create_result = runner.invoke(app, [
            "habit", "create",
            "--routine", routine_id,
            "-t", "Keep Me", "-r", "WEDNESDAY", "-s", "06:00", "-e", "07:00"
        ])

        import re
        id_line = [line for line in create_result.stdout.split("\n") if "ID:" in line][0]
        clean = re.sub(r'\x1b\[[0-9;]*m', '', id_line)
        habit_id = clean.split(":")[1].strip()

        result = runner.invoke(app, ["habit", "delete", habit_id], input="n\n")

        assert result.exit_code == 0
