"""
Integration tests para comandos de tasks.

Testa comandos CLI relacionados a criação, listagem, início, conclusão
e deleção de tasks (tarefas pontuais com deadline).

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
"""

from datetime import datetime, timedelta

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


class TestBRTaskCreation:
    """
    Integration: Criação de tasks via CLI (BR-TASK-CMD-CREATE-*).

    Valida criação de tasks com diferentes configurações,
    validação de datetime e persistência de campos opcionais.

    BRs cobertas:
    - BR-TASK-CMD-CREATE-001: Criação básica
    - BR-TASK-CMD-CREATE-002: Com descrição
    - BR-TASK-CMD-CREATE-003: Com cor
    - BR-TASK-CMD-CREATE-004: Rejeita datetime inválido
    """

    def test_br_task_cmd_create_001_basic(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema cria task básica com sucesso.

        DADO: Comando task create com título e datetime válidos
        QUANDO: Usuário cria task simples
        ENTÃO: Sistema retorna sucesso
        E: Mensagem confirma criação
        E: Título aparece na saída

        Referências:
            - BR-TASK-CMD-CREATE-001: Criação básica
        """
        # ARRANGE
        dt = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
        # ACT
        result = runner.invoke(
            app, ["task", "create", "--title", "Test Task", "--datetime", dt]
        )
        # ASSERT
        assert result.exit_code == 0, "Criação deve ter sucesso"
        assert "Tarefa criada com sucesso" in result.stdout
        assert "Test Task" in result.stdout

    def test_br_task_cmd_create_002_with_description(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema cria task com descrição opcional.

        DADO: Comando task create com flag --desc
        QUANDO: Usuário fornece descrição
        ENTÃO: Descrição é persistida e exibida

        Referências:
            - BR-TASK-CMD-CREATE-002: Com descrição
        """
        # ARRANGE
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        # ACT
        result = runner.invoke(
            app,
            [
                "task",
                "create",
                "-t",
                "Task with Desc",
                "-D",
                dt,
                "--desc",
                "Test description",
            ],
        )
        # ASSERT
        assert result.exit_code == 0
        assert "Test description" in result.stdout

    def test_br_task_cmd_create_003_with_color(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema cria task com cor personalizada.

        DADO: Comando task create com flag -c
        QUANDO: Usuário especifica cor
        ENTÃO: Cor é persistida e exibida

        Referências:
            - BR-TASK-CMD-CREATE-003: Com cor
        """
        # ARRANGE
        dt = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
        # ACT
        result = runner.invoke(
            app, ["task", "create", "-t", "Colored Task", "-D", dt, "-c", "blue"]
        )
        # ASSERT
        assert result.exit_code == 0
        assert "blue" in result.stdout

    def test_br_task_cmd_create_004_invalid_datetime(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema rejeita datetime inválido.

        DADO: Comando task create com datetime malformado
        QUANDO: Usuário fornece "invalid-date"
        ENTÃO: Sistema retorna erro (exit_code 1)

        Referências:
            - BR-TASK-CMD-CREATE-004: Rejeita datetime inválido
        """
        # ACT
        result = runner.invoke(
            app, ["task", "create", "-t", "Bad Date", "-D", "invalid-date"]
        )
        # ASSERT
        assert result.exit_code == 1, "Datetime inválido deve causar erro"


class TestBRTaskListing:
    """
    Integration: Listagem de tasks via CLI (BR-TASK-CMD-LIST-*).

    Valida listagem de tasks com diferentes filtros:
    vazio, múltiplas tasks, apenas pendentes, range de datas.

    BRs cobertas:
    - BR-TASK-CMD-LIST-001: Lista vazia
    - BR-TASK-CMD-LIST-002: Múltiplas tasks
    - BR-TASK-CMD-LIST-003: Filtro de pendentes
    - BR-TASK-CMD-LIST-004: Range de datas
    """

    def test_br_task_cmd_list_001_empty(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema lista vazio graciosamente.

        DADO: Nenhuma task no banco
        QUANDO: Usuário lista tasks
        ENTÃO: Mensagem "Nenhuma tarefa encontrada"

        Referências:
            - BR-TASK-CMD-LIST-001: Lista vazia
        """
        # ACT
        result = runner.invoke(app, ["task", "list"])
        # ASSERT
        assert result.exit_code == 0
        assert "Nenhuma tarefa encontrada" in result.stdout

    def test_br_task_cmd_list_002_with_tasks(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema lista múltiplas tasks.

        DADO: Duas tasks criadas
        QUANDO: Usuário lista tasks
        ENTÃO: Ambas aparecem na saída

        Referências:
            - BR-TASK-CMD-LIST-002: Múltiplas tasks
        """
        # ARRANGE
        dt1 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        dt2 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
        runner.invoke(app, ["task", "create", "-t", "Task 1", "-D", dt1])
        runner.invoke(app, ["task", "create", "-t", "Task 2", "-D", dt2])
        # ACT
        result = runner.invoke(app, ["task", "list"])
        # ASSERT
        assert result.exit_code == 0
        assert "Task 1" in result.stdout
        assert "Task 2" in result.stdout

    def test_br_task_cmd_list_003_pending_only(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Filtro --pending lista apenas pendentes.

        DADO: Task pendente criada
        QUANDO: Usuário lista com --pending
        ENTÃO: Task aparece sob seção "Pendentes"

        Referências:
            - BR-TASK-CMD-LIST-003: Filtro de pendentes
        """
        # ARRANGE
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        runner.invoke(app, ["task", "create", "-t", "Pending Task", "-D", dt])
        # ACT
        result = runner.invoke(app, ["task", "list", "--pending"])
        # ASSERT
        assert result.exit_code == 0
        assert "Pendentes" in result.stdout
        assert "Pending Task" in result.stdout

    def test_br_task_cmd_list_004_date_range(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Filtro --from/--to limita por datas.

        DADO: Task futura criada
        QUANDO: Usuário lista com range que inclui a task
        ENTÃO: Comando executa com sucesso

        Referências:
            - BR-TASK-CMD-LIST-004: Range de datas
        """
        # ARRANGE
        now = datetime.now()
        dt1 = (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
        runner.invoke(app, ["task", "create", "-t", "Future Task", "-D", dt1])
        start = now.strftime("%Y-%m-%d %H:%M")
        end = (now + timedelta(days=7)).strftime("%Y-%m-%d %H:%M")
        # ACT
        result = runner.invoke(app, ["task", "list", "--from", start, "--to", end])
        # ASSERT
        assert result.exit_code == 0


class TestBRTaskStart:
    """
    Integration: Iniciar tasks via CLI (BR-TASK-CMD-START-*).

    Valida início de tasks, detecção de tasks já iniciadas
    e tratamento de IDs inválidos.

    BRs cobertas:
    - BR-TASK-CMD-START-001: Inicia task pendente
    - BR-TASK-CMD-START-002: Detecta já iniciada
    - BR-TASK-CMD-START-003: Rejeita ID inválido
    """

    def test_br_task_cmd_start_001_task(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema inicia task pendente.

        DADO: Task criada (pendente)
        QUANDO: Usuário executa task start <id>
        ENTÃO: Mensagem "Tarefa iniciada"

        Referências:
            - BR-TASK-CMD-START-001: Inicia task
        """
        # ARRANGE
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        create_result = runner.invoke(
            app, ["task", "create", "-t", "Start Test", "-D", dt]
        )
        id_line = [line for line in create_result.stdout.split("\n") if "ID:" in line][
            0
        ]
        task_id = id_line.split(":")[1].strip()
        # ACT
        result = runner.invoke(app, ["task", "start", task_id])
        # ASSERT
        assert result.exit_code == 0
        assert "Tarefa iniciada" in result.stdout

    def test_br_task_cmd_start_002_already_started(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema detecta task já iniciada.

        DADO: Task já iniciada
        QUANDO: Usuário tenta iniciar novamente
        ENTÃO: Mensagem "já foi iniciada"

        Referências:
            - BR-TASK-CMD-START-002: Detecta já iniciada
        """
        # ARRANGE
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        create_result = runner.invoke(
            app, ["task", "create", "-t", "Already Started", "-D", dt]
        )
        id_line = [line for line in create_result.stdout.split("\n") if "ID:" in line][
            0
        ]
        task_id = id_line.split(":")[1].strip()
        runner.invoke(app, ["task", "start", task_id])
        # ACT
        result = runner.invoke(app, ["task", "start", task_id])
        # ASSERT
        assert result.exit_code == 0
        assert "já foi iniciada" in result.stdout

    def test_br_task_cmd_start_003_invalid_id(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema rejeita ID inválido.

        DADO: ID 999 que não existe
        QUANDO: Usuário tenta iniciar
        ENTÃO: Erro (exit_code 1)

        Referências:
            - BR-TASK-CMD-START-003: Rejeita ID inválido
        """
        # ACT
        result = runner.invoke(app, ["task", "start", "999"])
        # ASSERT
        assert result.exit_code == 1


class TestBRTaskCheck:
    """
    Integration: Marcar tasks como concluídas (BR-TASK-CMD-CHECK-*).

    Valida conclusão de tasks, cálculo de timing (atraso/antecipação)
    e tratamento de IDs inválidos.

    BRs cobertas:
    - BR-TASK-CMD-CHECK-001: Marca como concluída
    - BR-TASK-CMD-CHECK-002: Exibe timing
    - BR-TASK-CMD-CHECK-003: Rejeita ID inválido
    """

    def test_br_task_cmd_check_001_task(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema marca task como concluída.

        DADO: Task existente
        QUANDO: Usuário executa task check <id>
        ENTÃO: Mensagem "Tarefa concluída"

        Referências:
            - BR-TASK-CMD-CHECK-001: Marca concluída
        """
        # ARRANGE
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        create_result = runner.invoke(
            app, ["task", "create", "-t", "Complete Me", "-D", dt]
        )
        id_line = [line for line in create_result.stdout.split("\n") if "ID:" in line][
            0
        ]
        task_id = id_line.split(":")[1].strip()
        # ACT
        result = runner.invoke(app, ["task", "check", task_id])
        # ASSERT
        assert result.exit_code == 0
        assert "Tarefa concluída" in result.stdout

    def test_br_task_cmd_check_002_shows_timing(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema calcula e exibe timing.

        DADO: Task com deadline no passado
        QUANDO: Usuário marca como concluída
        ENTÃO: Saída mostra atraso/antecipação/no horário

        Referências:
            - BR-TASK-CMD-CHECK-002: Exibe timing
        """
        # ARRANGE
        dt = (datetime.now() - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M")
        create_result = runner.invoke(
            app, ["task", "create", "-t", "Late Task", "-D", dt]
        )
        id_line = [line for line in create_result.stdout.split("\n") if "ID:" in line][
            0
        ]
        task_id = id_line.split(":")[1].strip()
        # ACT
        result = runner.invoke(app, ["task", "check", task_id])
        # ASSERT
        assert result.exit_code == 0
        assert (
            "atraso" in result.stdout
            or "antecipação" in result.stdout
            or "No horário" in result.stdout
        )

    def test_br_task_cmd_check_003_invalid_id(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema rejeita ID inválido.

        DADO: ID 999 que não existe
        QUANDO: Usuário tenta marcar como concluída
        ENTÃO: Erro (exit_code 1)

        Referências:
            - BR-TASK-CMD-CHECK-003: Rejeita ID inválido
        """
        # ACT
        result = runner.invoke(app, ["task", "check", "999"])
        # ASSERT
        assert result.exit_code == 1


class TestBRTaskDeletion:
    """
    Integration: Deleção de tasks via CLI (BR-TASK-CMD-DELETE-*).

    Valida deleção com flag --force, com confirmação,
    cancelamento e tratamento de IDs inválidos.

    BRs cobertas:
    - BR-TASK-CMD-DELETE-001: Deleta com --force
    - BR-TASK-CMD-DELETE-002: Deleta com confirmação
    - BR-TASK-CMD-DELETE-003: Cancela deleção
    - BR-TASK-CMD-DELETE-004: Rejeita ID inválido
    """

    def test_br_task_cmd_delete_001_with_force(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema deleta task com --force.

        DADO: Task existente
        QUANDO: Usuário executa delete com --force
        ENTÃO: Deleta sem pedir confirmação

        Referências:
            - BR-TASK-CMD-DELETE-001: Deleta com force
        """
        # ARRANGE
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        create_result = runner.invoke(
            app, ["task", "create", "-t", "Delete Me", "-D", dt]
        )
        id_line = [line for line in create_result.stdout.split("\n") if "ID:" in line][
            0
        ]
        task_id = id_line.split(":")[1].strip()
        # ACT
        result = runner.invoke(app, ["task", "delete", task_id, "--force"])
        # ASSERT
        assert result.exit_code == 0
        assert "Tarefa deletada" in result.stdout

    def test_br_task_cmd_delete_002_with_confirmation(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema deleta task com confirmação 'y'.

        DADO: Task existente
        QUANDO: Usuário responde 'y' na confirmação
        ENTÃO: Task é deletada

        Referências:
            - BR-TASK-CMD-DELETE-002: Deleta com confirmação
        """
        # ARRANGE
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        create_result = runner.invoke(
            app, ["task", "create", "-t", "Delete Confirm", "-D", dt]
        )
        id_line = [line for line in create_result.stdout.split("\n") if "ID:" in line][
            0
        ]
        task_id = id_line.split(":")[1].strip()
        # ACT
        result = runner.invoke(app, ["task", "delete", task_id], input="y\n")
        # ASSERT
        assert result.exit_code == 0
        assert "Tarefa deletada" in result.stdout

    def test_br_task_cmd_delete_003_cancel(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema preserva task quando usuário cancela.

        DADO: Task existente
        QUANDO: Usuário responde 'n' na confirmação
        ENTÃO: Task não é deletada

        Referências:
            - BR-TASK-CMD-DELETE-003: Cancela deleção
        """
        # ARRANGE
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        create_result = runner.invoke(
            app, ["task", "create", "-t", "Keep Me", "-D", dt]
        )
        id_line = [line for line in create_result.stdout.split("\n") if "ID:" in line][
            0
        ]
        task_id = id_line.split(":")[1].strip()
        # ACT
        result = runner.invoke(app, ["task", "delete", task_id], input="n\n")
        # ASSERT
        assert result.exit_code == 0
        assert "Cancelado" in result.stdout

    def test_br_task_cmd_delete_004_invalid_id(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema rejeita ID inválido.

        DADO: ID 999 que não existe
        QUANDO: Usuário tenta deletar
        ENTÃO: Erro (exit_code 1)

        Referências:
            - BR-TASK-CMD-DELETE-004: Rejeita ID inválido
        """
        # ACT
        result = runner.invoke(app, ["task", "delete", "999", "--force"])
        # ASSERT
        assert result.exit_code == 1
