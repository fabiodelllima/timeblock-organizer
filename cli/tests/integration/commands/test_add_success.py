"""
Integration tests for add command - success cases.

Testa cenários de sucesso na criação de eventos/tasks,
validando persistência correta no banco de dados.

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
"""

from sqlmodel import Session, select
from typer.testing import CliRunner

from src.timeblock.database import get_engine
from src.timeblock.main import app
from src.timeblock.models import Event


class TestBRTaskCreationSuccess:
    """
    Integration: Criação bem-sucedida de tasks (BR-TASK-CREATE-*).

    Valida que o sistema cria e persiste eventos corretamente
    em diferentes cenários de uso.

    BRs cobertas:
    - BR-TASK-CREATE-001: Criação básica de evento
    - BR-TASK-CREATE-002: Criação com descrição opcional
    - BR-TASK-CREATE-003: Criação com cor personalizada
    - BR-TASK-CREATE-004: Criação com todos os campos
    - BR-TASK-CREATE-005: Múltiplos eventos sequenciais
    - BR-TASK-CREATE-006: Horários com minutos específicos
    """

    def test_br_task_create_001_basic_event(self, isolated_db: None, cli_runner: CliRunner) -> None:
        """
        Integration: Sistema cria evento básico com sucesso.

        DADO: Comando add com título e horários obrigatórios
        QUANDO: Usuário cria evento simples
        ENTÃO: Sistema retorna sucesso (exit_code 0)
        E: Evento é persistido no banco com dados corretos

        Referências:
            - BR-TASK-CREATE-001: Criação básica de evento
        """
        # ACT
        result = cli_runner.invoke(
            app,
            ["add", "Morning Meeting", "-s", "09:00", "-e", "10:00"],
        )

        # ASSERT
        assert result.exit_code == 0, "Criação deve ter sucesso"

        with Session(get_engine()) as session:
            events = session.exec(select(Event)).all()
            assert len(events) == 1, "Deve criar exatamente 1 evento"
            assert events[0].title == "Morning Meeting", "Título deve ser preservado"

    def test_br_task_create_002_with_description(
        self, isolated_db: None, cli_runner: CliRunner
    ) -> None:
        """
        Integration: Sistema cria evento com descrição opcional.

        DADO: Comando add com flag --desc
        QUANDO: Usuário fornece descrição
        ENTÃO: Sistema persiste descrição corretamente

        Referências:
            - BR-TASK-CREATE-002: Criação com descrição opcional
        """
        # ACT
        result = cli_runner.invoke(
            app,
            [
                "add",
                "Team Standup",
                "-s",
                "10:00",
                "-e",
                "10:30",
                "--desc",
                "Daily sync meeting",
            ],
        )

        # ASSERT
        assert result.exit_code == 0, "Criação com descrição deve ter sucesso"

        with Session(get_engine()) as session:
            event = session.exec(select(Event)).first()
            assert event is not None, "Evento deve existir"
            assert event.description == "Daily sync meeting", "Descrição deve ser preservada"

    def test_br_task_create_003_with_color(self, isolated_db: None, cli_runner: CliRunner) -> None:
        """
        Integration: Sistema cria evento com cor personalizada.

        DADO: Comando add com flag --color e formato hexadecimal válido
        QUANDO: Usuário especifica cor (#FF5733)
        ENTÃO: Sistema persiste cor corretamente

        Referências:
            - BR-TASK-CREATE-003: Criação com cor personalizada
        """
        # ACT
        result = cli_runner.invoke(
            app,
            [
                "add",
                "Focus Time",
                "-s",
                "14:00",
                "-e",
                "16:00",
                "--color",
                "#FF5733",
            ],
        )

        # ASSERT
        assert result.exit_code == 0, "Criação com cor deve ter sucesso"

        with Session(get_engine()) as session:
            event = session.exec(select(Event)).first()
            assert event is not None, "Evento deve existir"
            assert event.color == "#FF5733", "Cor deve ser preservada"

    def test_br_task_create_004_with_all_fields(
        self, isolated_db: None, cli_runner: CliRunner
    ) -> None:
        """
        Integration: Sistema cria evento com todos os campos opcionais.

        DADO: Comando add com descrição E cor
        QUANDO: Usuário fornece todos os campos
        ENTÃO: Sistema persiste todos os campos corretamente

        Referências:
            - BR-TASK-CREATE-004: Criação com todos os campos
        """
        # ACT
        result = cli_runner.invoke(
            app,
            [
                "add",
                "Client Call",
                "-s",
                "15:00",
                "-e",
                "16:00",
                "--desc",
                "Q3 Review",
                "--color",
                "#3498db",
            ],
        )

        # ASSERT
        assert result.exit_code == 0, "Criação completa deve ter sucesso"

        with Session(get_engine()) as session:
            event = session.exec(select(Event)).first()
            assert event is not None, "Evento deve existir"
            assert event.title == "Client Call", "Título deve ser preservado"
            assert event.description == "Q3 Review", "Descrição deve ser preservada"
            assert event.color == "#3498db", "Cor deve ser preservada"

    def test_br_task_create_005_multiple_events(
        self, isolated_db: None, cli_runner: CliRunner
    ) -> None:
        """
        Integration: Sistema cria múltiplos eventos sequenciais.

        DADO: Três comandos add executados sequencialmente
        QUANDO: Usuário cria múltiplos eventos
        ENTÃO: Sistema persiste todos os eventos
        E: Total de eventos no banco é 3

        Referências:
            - BR-TASK-CREATE-005: Múltiplos eventos sequenciais
        """
        # ACT
        cli_runner.invoke(app, ["add", "Event 1", "-s", "09:00", "-e", "10:00"])
        cli_runner.invoke(app, ["add", "Event 2", "-s", "11:00", "-e", "12:00"])
        cli_runner.invoke(app, ["add", "Event 3", "-s", "14:00", "-e", "15:00"])

        # ASSERT
        with Session(get_engine()) as session:
            events = session.exec(select(Event)).all()
            assert len(events) == 3, "Deve criar exatamente 3 eventos"

    def test_br_task_create_006_with_minutes(
        self, isolated_db: None, cli_runner: CliRunner
    ) -> None:
        """
        Integration: Sistema manuseia horários com minutos específicos.

        DADO: Comando add com horários incluindo minutos (10:15, 10:45)
        QUANDO: Usuário especifica minutos não-zero
        ENTÃO: Sistema persiste minutos corretamente
        E: Hora e minuto são exatos

        Referências:
            - BR-TASK-CREATE-006: Horários com minutos específicos
        """
        # ACT
        result = cli_runner.invoke(
            app,
            ["add", "Quick Sync", "-s", "10:15", "-e", "10:45"],
        )

        # ASSERT
        assert result.exit_code == 0, "Criação com minutos deve ter sucesso"

        with Session(get_engine()) as session:
            event = session.exec(select(Event)).first()
            assert event is not None, "Evento deve existir"
            assert event.scheduled_start.hour == 10, "Hora de início deve ser 10"
            assert event.scheduled_start.minute == 15, "Minuto de início deve ser 15"
            assert event.scheduled_end.hour == 10, "Hora de término deve ser 10"
            assert event.scheduled_end.minute == 45, "Minuto de término deve ser 45"
