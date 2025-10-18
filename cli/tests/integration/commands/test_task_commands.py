"""Testes de integração para comandos task."""

from datetime import datetime, timedelta

import pytest
from typer.testing import CliRunner

from src.timeblock.main import app


@pytest.fixture
def runner():
    return CliRunner()


class TestTaskCreate:
    """Testes para task create."""

    def test_create_basic(self, runner, isolated_db):
        dt = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
        result = runner.invoke(app, ["task", "create", "--title", "Test Task", "--datetime", dt])

        assert result.exit_code == 0
        assert "Tarefa criada com sucesso" in result.stdout
        assert "Test Task" in result.stdout

    def test_create_with_description(self, runner, isolated_db):
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        result = runner.invoke(
            app, ["task", "create", "-t", "Task with Desc", "-D", dt, "--desc", "Test description"]
        )

        assert result.exit_code == 0
        assert "Test description" in result.stdout

    def test_create_with_color(self, runner, isolated_db):
        dt = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
        result = runner.invoke(
            app, ["task", "create", "-t", "Colored Task", "-D", dt, "-c", "blue"]
        )

        assert result.exit_code == 0
        assert "blue" in result.stdout

    def test_create_invalid_datetime(self, runner, isolated_db):
        result = runner.invoke(app, ["task", "create", "-t", "Bad Date", "-D", "invalid-date"])

        assert result.exit_code == 1


class TestTaskList:
    """Testes para task list."""

    def test_list_empty(self, runner, isolated_db):
        result = runner.invoke(app, ["task", "list"])

        assert result.exit_code == 0
        assert "Nenhuma tarefa encontrada" in result.stdout

    def test_list_with_tasks(self, runner, isolated_db):
        dt1 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        dt2 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")

        runner.invoke(app, ["task", "create", "-t", "Task 1", "-D", dt1])
        runner.invoke(app, ["task", "create", "-t", "Task 2", "-D", dt2])

        result = runner.invoke(app, ["task", "list"])

        assert result.exit_code == 0
        assert "Task 1" in result.stdout
        assert "Task 2" in result.stdout

    def test_list_pending_only(self, runner, isolated_db):
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        runner.invoke(app, ["task", "create", "-t", "Pending Task", "-D", dt])

        result = runner.invoke(app, ["task", "list", "--pending"])

        assert result.exit_code == 0
        assert "Pendentes" in result.stdout
        assert "Pending Task" in result.stdout

    def test_list_date_range(self, runner, isolated_db):
        now = datetime.now()
        dt1 = (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")

        runner.invoke(app, ["task", "create", "-t", "Future Task", "-D", dt1])

        start = now.strftime("%Y-%m-%d %H:%M")
        end = (now + timedelta(days=7)).strftime("%Y-%m-%d %H:%M")

        result = runner.invoke(app, ["task", "list", "--from", start, "--to", end])

        assert result.exit_code == 0


class TestTaskStart:
    """Testes para task start."""

    def test_start_task(self, runner, isolated_db):
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        create_result = runner.invoke(app, ["task", "create", "-t", "Start Test", "-D", dt])

        id_line = [line for line in create_result.stdout.split("\n") if "ID:" in line][0]
        task_id = id_line.split(":")[1].strip()

        result = runner.invoke(app, ["task", "start", task_id])

        assert result.exit_code == 0
        assert "Tarefa iniciada" in result.stdout

    def test_start_already_started(self, runner, isolated_db):
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        create_result = runner.invoke(app, ["task", "create", "-t", "Already Started", "-D", dt])

        id_line = [line for line in create_result.stdout.split("\n") if "ID:" in line][0]
        task_id = id_line.split(":")[1].strip()

        runner.invoke(app, ["task", "start", task_id])

        result = runner.invoke(app, ["task", "start", task_id])

        assert result.exit_code == 0
        assert "já foi iniciada" in result.stdout

    def test_start_invalid_id(self, runner, isolated_db):
        result = runner.invoke(app, ["task", "start", "999"])

        assert result.exit_code == 1


class TestTaskCheck:
    """Testes para task check."""

    def test_check_task(self, runner, isolated_db):
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        create_result = runner.invoke(app, ["task", "create", "-t", "Complete Me", "-D", dt])

        id_line = [line for line in create_result.stdout.split("\n") if "ID:" in line][0]
        task_id = id_line.split(":")[1].strip()

        result = runner.invoke(app, ["task", "check", task_id])

        assert result.exit_code == 0
        assert "Tarefa concluída" in result.stdout

    def test_check_shows_timing(self, runner, isolated_db):
        dt = (datetime.now() - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M")
        create_result = runner.invoke(app, ["task", "create", "-t", "Late Task", "-D", dt])

        id_line = [line for line in create_result.stdout.split("\n") if "ID:" in line][0]
        task_id = id_line.split(":")[1].strip()

        result = runner.invoke(app, ["task", "check", task_id])

        assert result.exit_code == 0
        assert (
            "atraso" in result.stdout
            or "antecipação" in result.stdout
            or "No horário" in result.stdout
        )

    def test_check_invalid_id(self, runner, isolated_db):
        result = runner.invoke(app, ["task", "check", "999"])

        assert result.exit_code == 1


class TestTaskDelete:
    """Testes para task delete."""

    def test_delete_with_force(self, runner, isolated_db):
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        create_result = runner.invoke(app, ["task", "create", "-t", "Delete Me", "-D", dt])

        id_line = [line for line in create_result.stdout.split("\n") if "ID:" in line][0]
        task_id = id_line.split(":")[1].strip()

        result = runner.invoke(app, ["task", "delete", task_id, "--force"])

        assert result.exit_code == 0
        assert "Tarefa deletada" in result.stdout

    def test_delete_with_confirmation(self, runner, isolated_db):
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        create_result = runner.invoke(app, ["task", "create", "-t", "Delete Confirm", "-D", dt])

        id_line = [line for line in create_result.stdout.split("\n") if "ID:" in line][0]
        task_id = id_line.split(":")[1].strip()

        result = runner.invoke(app, ["task", "delete", task_id], input="y\n")

        assert result.exit_code == 0
        assert "Tarefa deletada" in result.stdout

    def test_delete_cancel(self, runner, isolated_db):
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        create_result = runner.invoke(app, ["task", "create", "-t", "Keep Me", "-D", dt])

        id_line = [line for line in create_result.stdout.split("\n") if "ID:" in line][0]
        task_id = id_line.split(":")[1].strip()

        result = runner.invoke(app, ["task", "delete", task_id], input="n\n")

        assert result.exit_code == 0
        assert "Cancelado" in result.stdout

    def test_delete_invalid_id(self, runner, isolated_db):
        result = runner.invoke(app, ["task", "delete", "999", "--force"])

        assert result.exit_code == 1
