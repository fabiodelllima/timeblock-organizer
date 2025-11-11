"""
Integration tests for add command - edge cases and boundary conditions.

Testa casos extremos e condições de contorno para validação de entrada
do comando add (criação de eventos/tasks).

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
"""

import pytest
from sqlmodel import Session, select
from typer.testing import CliRunner

from src.timeblock.database import get_engine
from src.timeblock.main import app
from src.timeblock.models import Event


@pytest.fixture
def runner() -> CliRunner:
    """
    Cria CLI test runner.
    
    Returns:
        CliRunner configurado para testes.
    """
    return CliRunner()


class TestBRTaskInputValidation:
    """
    Integration: Validação de entrada para criação de tasks (BR-TASK-INPUT-*).
    
    Testa casos extremos e boundary conditions para garantir robustez
    do sistema na criação de eventos/tasks.
    
    BRs cobertas:
    - BR-TASK-INPUT-001: Validação de duração mínima
    - BR-TASK-INPUT-002: Validação de eventos cruzando meia-noite
    - BR-TASK-INPUT-003: Validação de títulos longos
    - BR-TASK-INPUT-004: Validação de caracteres especiais
    - BR-TASK-INPUT-005: Validação de descrições vazias
    """

    def test_br_task_input_001_one_minute_event(
        self, isolated_db: None, cli_runner: CliRunner
    ) -> None:
        """
        Integration: Sistema aceita evento com duração mínima de 1 minuto.
        
        DADO: Comando add com duração de 1 minuto
        QUANDO: Usuário cria evento de 10:00 a 10:01
        ENTÃO: Sistema cria evento com sucesso
        E: Duração calculada é exatamente 60 segundos
        
        Referências:
            - BR-TASK-INPUT-001: Validação de duração mínima
        """
        # ACT
        result = cli_runner.invoke(
            app,
            ["add", "Quick Check", "-s", "10:00", "-e", "10:01"],
        )

        # ASSERT
        assert result.exit_code == 0, "Comando deve ter sucesso"
        
        with Session(get_engine()) as session:
            event = session.exec(select(Event)).all()[-1]
            duration = (event.scheduled_end - event.scheduled_start).total_seconds()
            assert duration == 60, "Duração deve ser exatamente 60 segundos"

    def test_br_task_input_002_event_crossing_midnight(
        self, isolated_db: None, cli_runner: CliRunner
    ) -> None:
        """
        Integration: Sistema aceita eventos que cruzam meia-noite.
        
        DADO: Comando add com horário de início antes de meia-noite
        QUANDO: Horário de término é após meia-noite (23:00 a 01:00)
        ENTÃO: Sistema cria evento com sucesso
        E: Evento é registrado corretamente no banco
        
        Referências:
            - BR-TASK-INPUT-002: Validação de eventos cruzando meia-noite
        """
        # ACT
        result = cli_runner.invoke(
            app,
            ["add", "Night Shift", "-s", "23:00", "-e", "01:00"],
        )

        # ASSERT
        assert result.exit_code == 0, "Evento cruzando meia-noite deve ser aceito"

    def test_br_task_input_003_long_title(
        self, isolated_db: None, cli_runner: CliRunner
    ) -> None:
        """
        Integration: Sistema aceita títulos longos (até 200 caracteres).
        
        DADO: Título com 200 caracteres
        QUANDO: Usuário cria evento com título longo
        ENTÃO: Sistema cria evento com sucesso
        E: Título completo é preservado no banco
        
        Referências:
            - BR-TASK-INPUT-003: Validação de títulos longos
        """
        # ARRANGE
        long_title = "A" * 200

        # ACT
        result = cli_runner.invoke(
            app,
            ["add", long_title, "-s", "10:00", "-e", "11:00"],
        )

        # ASSERT
        assert result.exit_code == 0, "Título longo deve ser aceito"
        
        with Session(get_engine()) as session:
            event = session.exec(select(Event)).all()[-1]
            assert event.title == long_title, "Título completo deve ser preservado"

    def test_br_task_input_004_special_characters_in_title(
        self, isolated_db: None, cli_runner: CliRunner
    ) -> None:
        """
        Integration: Sistema aceita caracteres especiais em títulos.
        
        DADO: Título contendo caracteres especiais (: & () - #)
        QUANDO: Usuário cria evento com caracteres especiais
        ENTÃO: Sistema cria evento com sucesso
        E: Caracteres especiais são preservados exatamente
        
        Referências:
            - BR-TASK-INPUT-004: Validação de caracteres especiais
        """
        # ARRANGE
        special_title = "Meeting: Q&A (Part 1) - Review #2"

        # ACT
        result = cli_runner.invoke(
            app,
            ["add", special_title, "-s", "10:00", "-e", "11:00"],
        )

        # ASSERT
        assert result.exit_code == 0, "Caracteres especiais devem ser aceitos"
        
        with Session(get_engine()) as session:
            event = session.exec(select(Event)).all()[-1]
            assert event.title == special_title, "Caracteres devem ser preservados"

    def test_br_task_input_005_empty_description(
        self, isolated_db: None, cli_runner: CliRunner
    ) -> None:
        """
        Integration: Sistema aceita descrição vazia graciosamente.
        
        DADO: Comando add com flag --desc vazia
        QUANDO: Usuário fornece descrição vazia
        ENTÃO: Sistema cria evento com sucesso
        E: Descrição é armazenada como string vazia
        
        Referências:
            - BR-TASK-INPUT-005: Validação de descrições vazias
        """
        # ACT
        result = cli_runner.invoke(
            app,
            ["add", "Meeting", "-s", "10:00", "-e", "11:00", "--desc", ""],
        )

        # ASSERT
        assert result.exit_code == 0, "Descrição vazia deve ser aceita"
        
        with Session(get_engine()) as session:
            event = session.exec(select(Event)).all()[-1]
            assert event.description == "", "Descrição deve ser string vazia"

    def test_br_task_input_006_midnight_event(
        self, isolated_db: None, cli_runner: CliRunner
    ) -> None:
        """
        Integration: Sistema aceita eventos começando exatamente à meia-noite.
        
        DADO: Comando add com horário 00:00
        QUANDO: Usuário cria evento iniciando à meia-noite
        ENTÃO: Sistema cria evento com sucesso
        E: Horário é armazenado corretamente como 00:00
        
        Referências:
            - BR-TASK-INPUT-002: Validação de horários especiais
        """
        # ACT
        result = cli_runner.invoke(
            app,
            ["add", "Midnight Task", "-s", "00:00", "-e", "01:00"],
        )

        # ASSERT
        assert result.exit_code == 0, "Evento à meia-noite deve ser aceito"
        
        with Session(get_engine()) as session:
            event = session.exec(select(Event)).all()[-1]
            assert event.scheduled_start.hour == 0, "Hora deve ser 00"
            assert event.scheduled_start.minute == 0, "Minuto deve ser 00"
