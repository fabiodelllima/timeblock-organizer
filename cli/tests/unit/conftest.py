"""Fixtures específicas para unit tests."""

from datetime import date, time
from unittest.mock import MagicMock, Mock

import pytest


@pytest.fixture
def mock_session():
    """Mock de sessão de database."""
    session = MagicMock()
    session.add = Mock()
    session.commit = Mock()
    session.refresh = Mock()
    return session


@pytest.fixture
def sample_date():
    """Data de exemplo para testes."""
    return date(2025, 10, 17)


@pytest.fixture
def sample_time_start():
    """Hora de início exemplo."""
    return time(9, 0)


@pytest.fixture
def sample_time_end():
    """Hora de fim exemplo."""
    return time(10, 0)
