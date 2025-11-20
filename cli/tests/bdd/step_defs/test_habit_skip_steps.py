"""Step definitions para BR-HABIT-SKIP-001 (Skip de Habit com Categorização).

Conecta cenários Gherkin do arquivo habit_skip.feature com código Python.
"""

import pytest
from datetime import date, time
from pytest_bdd import scenarios, given, when, then, parsers
from sqlmodel import Session

from src.timeblock.models.routine import Routine
from src.timeblock.models.habit import Habit, Recurrence
from src.timeblock.models.habit_instance import HabitInstance
from src.timeblock.models.time_log import TimeLog
from src.timeblock.models.enums import Status, NotDoneSubstatus, SkipReason
from src.timeblock.services.habit_instance_service import HabitInstanceService


# Carregar todos os cenários do arquivo
scenarios('../features/habit_skip.feature')


# ==================== CONTEXTO ====================

@given('que existe uma rotina "Rotina Matinal"', target_fixture='test_routine')
def criar_rotina(session: Session):
    """Cria rotina para testes."""
    routine = Routine(name="Rotina Matinal")
    session.add(routine)
    session.commit()
    session.refresh(routine)
    assert routine.id is not None
    return routine


@given('existe um habit "Academia" agendado para hoje às 07:00-08:30', target_fixture='test_habit')
def criar_habit(session: Session, test_routine: Routine):
    """Cria habit para testes."""
    assert test_routine.id is not None
    
    habit = Habit(
        routine_id=test_routine.id,
        title="Academia",
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 30),
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    assert habit.id is not None
    return habit


@given('existe uma HabitInstance com status "PENDING"', target_fixture='test_instance')
def criar_habit_instance(session: Session, test_habit: Habit):
    """Cria HabitInstance PENDING para testes."""
    assert test_habit.id is not None
    
    instance = HabitInstance(
        habit_id=test_habit.id,
        date=date.today(),
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 30),
        status=Status.PENDING,
    )
    session.add(instance)
    session.commit()
    session.refresh(instance)
    assert instance.id is not None
    return instance


# ==================== WHEN (AÇÕES) ====================

@when(parsers.parse('usuário marca skip com categoria "{category}" e nota "{note}"'))
def skip_com_nota(session: Session, test_instance: HabitInstance, category: str, note: str):
    """Executa skip com categoria e nota."""
    skip_reason = SkipReason[category]
    service = HabitInstanceService()
    
    result = service.skip_habit_instance(
        habit_instance_id=test_instance.id,
        skip_reason=skip_reason,
        skip_note=note,
        session=session
    )
    
    # Armazenar resultado no contexto
    session.info = {'result': result}  # type: ignore


@when(parsers.parse('usuário marca skip com categoria "{category}" sem nota'))
def skip_sem_nota(session: Session, test_instance: HabitInstance, category: str):
    """Executa skip com categoria sem nota."""
    skip_reason = SkipReason[category]
    service = HabitInstanceService()
    
    result = service.skip_habit_instance(
        habit_instance_id=test_instance.id,
        skip_reason=skip_reason,
        skip_note=None,
        session=session
    )
    
    session.info = {'result': result}  # type: ignore


@when('usuário tenta skip de HabitInstance com ID 99999')
def skip_id_inexistente(session: Session):
    """Tenta skip de ID inexistente."""
    service = HabitInstanceService()
    
    try:
        service.skip_habit_instance(
            habit_instance_id=99999,
            skip_reason=SkipReason.HEALTH,
            skip_note=None,
            session=session
        )
        session.info = {'error': None}  # type: ignore
    except ValueError as e:
        session.info = {'error': str(e)}  # type: ignore


@given('que skip_note tem 501 caracteres', target_fixture='nota_longa')
def nota_longa():
    """Cria nota com 501 caracteres."""
    return "A" * 501


@when(parsers.parse('usuário tenta skip com categoria "{category}" e essa nota'))
def skip_nota_longa(session: Session, test_instance: HabitInstance, category: str, nota_longa: str):
    """Tenta skip com nota muito longa."""
    skip_reason = SkipReason[category]
    service = HabitInstanceService()
    
    try:
        service.skip_habit_instance(
            habit_instance_id=test_instance.id,
            skip_reason=skip_reason,
            skip_note=nota_longa,
            session=session
        )
        session.info = {'error': None}  # type: ignore
    except ValueError as e:
        session.info = {'error': str(e)}  # type: ignore


# ==================== THEN (ASSERÇÕES) ====================

@then(parsers.parse('o status deve ser "{expected_status}"'))
def verificar_status(session: Session, test_instance: HabitInstance, expected_status: str):
    """Verifica status da instância."""
    session.refresh(test_instance)
    assert test_instance.status.value == expected_status.lower()


@then(parsers.parse('o substatus deve ser "{expected_substatus}"'))
def verificar_substatus(session: Session, test_instance: HabitInstance, expected_substatus: str):
    """Verifica substatus da instância."""
    session.refresh(test_instance)
    assert test_instance.not_done_substatus is not None
    assert test_instance.not_done_substatus.value == expected_substatus.lower()


@then(parsers.parse('o skip_reason deve ser "{expected_reason}"'))
def verificar_skip_reason(session: Session, test_instance: HabitInstance, expected_reason: str):
    """Verifica skip_reason."""
    session.refresh(test_instance)
    assert test_instance.skip_reason is not None
    assert test_instance.skip_reason.value == expected_reason


@then(parsers.parse('o skip_note deve ser "{expected_note}"'))
def verificar_skip_note(session: Session, test_instance: HabitInstance, expected_note: str):
    """Verifica skip_note."""
    session.refresh(test_instance)
    assert test_instance.skip_note == expected_note


@then('o skip_note deve ser NULL')
def verificar_skip_note_null(session: Session, test_instance: HabitInstance):
    """Verifica que skip_note é None."""
    session.refresh(test_instance)
    assert test_instance.skip_note is None


@then('done_substatus deve ser NULL')
def verificar_done_substatus_null(session: Session, test_instance: HabitInstance):
    """Verifica que done_substatus é None."""
    session.refresh(test_instance)
    assert test_instance.done_substatus is None


@then('completion_percentage deve ser NULL')
def verificar_completion_null(session: Session, test_instance: HabitInstance):
    """Verifica que completion_percentage é None."""
    session.refresh(test_instance)
    assert test_instance.completion_percentage is None


@then(parsers.parse('o sistema deve retornar erro "{expected_error}"'))
def verificar_erro(session: Session, expected_error: str):
    """Verifica mensagem de erro."""
    error = session.info.get('error')  # type: ignore
    assert error is not None, "Esperava erro mas não foi lançado"
    assert expected_error in error, f"Erro esperado: '{expected_error}', recebido: '{error}'"
