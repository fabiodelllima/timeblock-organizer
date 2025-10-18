"""Testes unitários para RoutineService - Operations."""

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


class TestActivateRoutine:
    """Testes para activate_routine."""

    def test_activate_routine_success(
        self, routine_service: RoutineService, mock_session: Mock
    ) -> None:
        """Testa ativação de rotina com sucesso."""
        routine_id = 1
        routine = Routine(
            id=routine_id,
            name="Test",
            is_active=False,
            created_at=datetime.now(),
        )
        mock_session.get.return_value = routine

        routine_service.activate_routine(routine_id)

        assert routine.is_active is True
        mock_session.add.assert_called_once_with(routine)
        mock_session.commit.assert_called_once()

    def test_activate_routine_not_found(
        self, routine_service: RoutineService, mock_session: Mock
    ) -> None:
        """Testa erro ao ativar rotina inexistente."""
        routine_id = 999
        mock_session.get.return_value = None

        with pytest.raises(ValueError, match=f"Rotina com ID {routine_id} não encontrada"):
            routine_service.activate_routine(routine_id)

        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()

    def test_activate_already_active_routine(
        self, routine_service: RoutineService, mock_session: Mock
    ) -> None:
        """Testa ativação de rotina já ativa (idempotente)."""
        routine_id = 1
        routine = Routine(
            id=routine_id,
            name="Test",
            is_active=True,
            created_at=datetime.now(),
        )
        mock_session.get.return_value = routine

        routine_service.activate_routine(routine_id)

        assert routine.is_active is True
        mock_session.add.assert_called_once_with(routine)
        mock_session.commit.assert_called_once()


class TestDeactivateRoutine:
    """Testes para deactivate_routine."""

    def test_deactivate_routine_success(
        self, routine_service: RoutineService, mock_session: Mock
    ) -> None:
        """Testa desativação de rotina com sucesso."""
        routine_id = 1
        routine = Routine(
            id=routine_id,
            name="Test",
            is_active=True,
            created_at=datetime.now(),
        )
        mock_session.get.return_value = routine

        routine_service.deactivate_routine(routine_id)

        assert routine.is_active is False
        mock_session.add.assert_called_once_with(routine)
        mock_session.commit.assert_called_once()

    def test_deactivate_routine_not_found(
        self, routine_service: RoutineService, mock_session: Mock
    ) -> None:
        """Testa erro ao desativar rotina inexistente."""
        routine_id = 999
        mock_session.get.return_value = None

        with pytest.raises(ValueError, match=f"Rotina com ID {routine_id} não encontrada"):
            routine_service.deactivate_routine(routine_id)

        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()

    def test_deactivate_already_inactive_routine(
        self, routine_service: RoutineService, mock_session: Mock
    ) -> None:
        """Testa desativação de rotina já inativa (idempotente)."""
        routine_id = 1
        routine = Routine(
            id=routine_id,
            name="Test",
            is_active=False,
            created_at=datetime.now(),
        )
        mock_session.get.return_value = routine

        routine_service.deactivate_routine(routine_id)

        assert routine.is_active is False
        mock_session.add.assert_called_once_with(routine)
        mock_session.commit.assert_called_once()


class TestDeleteRoutine:
    """Testes para delete_routine."""

    def test_delete_routine_success(
        self, routine_service: RoutineService, mock_session: Mock
    ) -> None:
        """Testa remoção de rotina com sucesso."""
        routine_id = 1
        routine = Routine(
            id=routine_id,
            name="Test",
            is_active=True,
            created_at=datetime.now(),
        )
        mock_session.get.return_value = routine

        routine_service.delete_routine(routine_id)

        mock_session.delete.assert_called_once_with(routine)
        mock_session.commit.assert_called_once()

    def test_delete_routine_not_found(
        self, routine_service: RoutineService, mock_session: Mock
    ) -> None:
        """Testa erro ao remover rotina inexistente."""
        routine_id = 999
        mock_session.get.return_value = None

        with pytest.raises(ValueError, match=f"Rotina com ID {routine_id} não encontrada"):
            routine_service.delete_routine(routine_id)

        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()
