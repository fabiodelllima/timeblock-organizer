"""Testes unitários para RoutineService - CRUD operations."""

from datetime import datetime
from unittest.mock import MagicMock, Mock

import pytest
from sqlmodel import Session

from src.timeblock.models import Routine
from src.timeblock.services.routine_service import RoutineService


@pytest.fixture
def mock_session() -> Mock:
    """Cria uma sessão mock para testes."""
    return MagicMock(spec=Session)


@pytest.fixture
def routine_service(mock_session: Mock) -> RoutineService:
    """Cria um RoutineService com sessão mock."""
    return RoutineService(mock_session)


class TestCreateRoutine:
    """Testes para create_routine."""

    def test_create_routine_success(
        self, routine_service: RoutineService, mock_session: Mock
    ) -> None:
        """Testa criação de rotina com sucesso."""
        name = "Rotina Matinal"
        routine = routine_service.create_routine(name)
        assert routine.name == name
        assert routine.is_active is False
        assert isinstance(routine.created_at, datetime)
        mock_session.add.assert_called_once()

    def test_create_routine_strips_whitespace(self, routine_service: RoutineService) -> None:
        """Testa que espaços em branco são removidos."""
        routine = routine_service.create_routine("  Rotina Noturna  ")
        assert routine.name == "Rotina Noturna"

    def test_create_routine_with_empty_name(self, routine_service: RoutineService) -> None:
        """Testa erro ao criar rotina com nome vazio."""
        with pytest.raises(ValueError, match="Nome da rotina não pode ser vazio"):
            routine_service.create_routine("")

    def test_create_routine_with_whitespace_only(self, routine_service: RoutineService) -> None:
        """Testa erro ao criar rotina com apenas espaços."""
        with pytest.raises(ValueError, match="Nome da rotina não pode ser vazio"):
            routine_service.create_routine("   ")

    def test_create_routine_with_name_too_long(self, routine_service: RoutineService) -> None:
        """Testa erro ao criar rotina com nome muito longo."""
        long_name = "a" * 201

        with pytest.raises(ValueError, match="Nome da rotina não pode ter mais de 200 caracteres"):
            routine_service.create_routine(long_name)

    def test_create_routine_with_max_length_name(self, routine_service: RoutineService) -> None:
        """Testa criação de rotina com nome no limite máximo."""
        max_name = "a" * 200
        routine = routine_service.create_routine(max_name)
        assert routine.name == max_name
        assert len(routine.name) == 200


class TestGetRoutine:
    """Testes para get_routine."""

    def test_get_routine_found(self, routine_service: RoutineService, mock_session: Mock) -> None:
        """Testa busca de rotina existente."""
        routine_id = 1
        expected_routine = Routine(
            id=routine_id,
            name="Test Routine",
            is_active=True,
            created_at=datetime.now(),
        )
        mock_session.get.return_value = expected_routine
        routine = routine_service.get_routine(routine_id)
        assert routine == expected_routine
        mock_session.get.assert_called_once_with(Routine, routine_id)

    def test_get_routine_not_found(
        self, routine_service: RoutineService, mock_session: Mock
    ) -> None:
        """Testa busca de rotina inexistente."""
        routine_id = 999
        mock_session.get.return_value = None
        routine = routine_service.get_routine(routine_id)
        assert routine is None
        mock_session.get.assert_called_once_with(Routine, routine_id)


class TestListRoutines:
    """Testes para list_routines."""

    def test_list_routines_active_only(
        self, routine_service: RoutineService, mock_session: Mock
    ) -> None:
        """Testa listagem apenas de rotinas ativas."""
        mock_result = Mock()
        mock_result.all.return_value = [
            Routine(id=1, name="Active 1", is_active=True, created_at=datetime.now()),
            Routine(id=2, name="Active 2", is_active=True, created_at=datetime.now()),
        ]
        mock_session.exec.return_value = mock_result
        routines = routine_service.list_routines(active_only=True)
        assert len(routines) == 2
        mock_session.exec.assert_called_once()

    def test_list_routines_all(self, routine_service: RoutineService, mock_session: Mock) -> None:
        """Testa listagem de todas as rotinas."""
        mock_result = Mock()
        mock_result.all.return_value = [
            Routine(id=1, name="Active", is_active=True, created_at=datetime.now()),
            Routine(id=2, name="Inactive", is_active=False, created_at=datetime.now()),
        ]
        mock_session.exec.return_value = mock_result
        routines = routine_service.list_routines(active_only=False)
        assert len(routines) == 2
        mock_session.exec.assert_called_once()

    def test_list_routines_empty(self, routine_service: RoutineService, mock_session: Mock) -> None:
        """Testa listagem quando não há rotinas."""
        mock_result = Mock()
        mock_result.all.return_value = []
        mock_session.exec.return_value = mock_result
        routines = routine_service.list_routines()
        assert routines == []
