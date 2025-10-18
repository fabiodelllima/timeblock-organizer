"""Teste de validação das fixtures de integração."""

from sqlalchemy import text


class TestFixtures:
    """Valida que as fixtures estão funcionando."""

    def test_integration_session_works(self, integration_session):
        """Testa que a sessão de integração funciona."""
        assert integration_session is not None
        result = integration_session.execute(text("SELECT 1"))
        assert result is not None

    def test_sample_routine_created(self, sample_routine):
        """Testa que rotina de exemplo foi criada."""
        assert sample_routine.id is not None
        assert sample_routine.name == "Test Routine"
        assert sample_routine.is_active is True

    def test_sample_habits_created(self, sample_habits):
        """Testa que hábitos de exemplo foram criados."""
        assert len(sample_habits) == 2
        assert sample_habits[0].title == "Exercise"
        assert sample_habits[1].title == "Reading"

    def test_sample_task_created(self, sample_task):
        """Testa que task de exemplo foi criada."""
        assert sample_task.id is not None
        assert sample_task.title == "Dentist Appointment"
