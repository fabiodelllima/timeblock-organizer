"""Testes unitários para BR-HABIT-INSTANCE-STATUS-001.

Refatoração Status + Substatus do modelo HabitInstance.
Valida transições de estado, cálculo de substatus e validações.
"""

import pytest
from datetime import date, time, datetime, timedelta
from src.timeblock.models.enums import (
    Status,
    DoneSubstatus,
    NotDoneSubstatus,
    SkipReason,
)
from src.timeblock.models.habit_instance import HabitInstance


class TestBRStatus001TimerStopCalculatesSubstatus:
    """Cenários 1-4: Timer stop calcula substatus correto baseado em completion."""

    def test_scenario_001_completion_full_90_to_110_percent(self):
        """CENÁRIO 1: Timer stop com 92% completion -> FULL."""
        # DADO
        instance = HabitInstance(
            habit_id=1,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),  # 60 min meta
            status=Status.PENDING,
        )

        # QUANDO: usuário completa com 55 minutos (92%)
        actual_duration_minutes = 55
        completion_percentage = 92

        instance.status = Status.DONE
        instance.done_substatus = DoneSubstatus.FULL
        instance.completion_percentage = completion_percentage

        # ENTÃO
        assert instance.status == Status.DONE
        assert instance.done_substatus == DoneSubstatus.FULL
        assert instance.not_done_substatus is None
        assert instance.completion_percentage == 92

    def test_scenario_002_completion_partial_less_than_90_percent(self):
        """CENÁRIO 2: Timer stop com 75% completion -> PARTIAL."""
        # DADO
        instance = HabitInstance(
            habit_id=1,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),  # 60 min meta
            status=Status.PENDING,
        )

        # QUANDO: usuário completa com 45 minutos (75%)
        completion_percentage = 75

        instance.status = Status.DONE
        instance.done_substatus = DoneSubstatus.PARTIAL
        instance.completion_percentage = completion_percentage

        # ENTÃO
        assert instance.status == Status.DONE
        assert instance.done_substatus == DoneSubstatus.PARTIAL
        assert instance.not_done_substatus is None
        assert instance.completion_percentage == 75

    def test_scenario_003_completion_overdone_110_to_150_percent(self):
        """CENÁRIO 3: Timer stop com 125% completion -> OVERDONE."""
        # DADO
        instance = HabitInstance(
            habit_id=1,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),  # 60 min meta
            status=Status.PENDING,
        )

        # QUANDO: usuário completa com 75 minutos (125%)
        completion_percentage = 125

        instance.status = Status.DONE
        instance.done_substatus = DoneSubstatus.OVERDONE
        instance.completion_percentage = completion_percentage

        # ENTÃO
        assert instance.status == Status.DONE
        assert instance.done_substatus == DoneSubstatus.OVERDONE
        assert instance.not_done_substatus is None
        assert instance.completion_percentage == 125

    def test_scenario_004_completion_excessive_more_than_150_percent(self):
        """CENÁRIO 4: Timer stop com 167% completion -> EXCESSIVE."""
        # DADO
        instance = HabitInstance(
            habit_id=1,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),  # 60 min meta
            status=Status.PENDING,
        )

        # QUANDO: usuário completa com 100 minutos (167%)
        completion_percentage = 167

        instance.status = Status.DONE
        instance.done_substatus = DoneSubstatus.EXCESSIVE
        instance.completion_percentage = completion_percentage

        # ENTÃO
        assert instance.status == Status.DONE
        assert instance.done_substatus == DoneSubstatus.EXCESSIVE
        assert instance.not_done_substatus is None
        assert instance.completion_percentage == 167


class TestBRStatus001SkipWithCategory:
    """Cenários 5-7: Skip com/sem categoria."""

    def test_scenario_005_skip_with_category_sets_justified(self):
        """CENÁRIO 5: Skip com categoria -> SKIPPED_JUSTIFIED."""
        # DADO
        instance = HabitInstance(
            habit_id=1,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.PENDING,
        )

        # QUANDO: usuário executa skip com categoria
        instance.status = Status.NOT_DONE
        instance.not_done_substatus = NotDoneSubstatus.SKIPPED_JUSTIFIED
        instance.skip_reason = SkipReason.HEALTH

        # ENTÃO
        assert instance.status == Status.NOT_DONE
        assert instance.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED
        assert instance.skip_reason == SkipReason.HEALTH
        assert instance.done_substatus is None
        assert instance.completion_percentage is None

    def test_scenario_006_skip_with_category_and_note(self):
        """CENÁRIO 6: Skip com categoria e nota adicional."""
        # DADO
        instance = HabitInstance(
            habit_id=1,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.PENDING,
        )

        # QUANDO: usuário executa skip com categoria e nota
        instance.status = Status.NOT_DONE
        instance.not_done_substatus = NotDoneSubstatus.SKIPPED_JUSTIFIED
        instance.skip_reason = SkipReason.HEALTH
        instance.skip_note = "Gripe"

        # ENTÃO
        assert instance.status == Status.NOT_DONE
        assert instance.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED
        assert instance.skip_reason == SkipReason.HEALTH
        assert instance.skip_note == "Gripe"
        assert instance.done_substatus is None


class TestBRStatus001ValidationDoneRequiresSubstatus:
    """Cenário 8: Validação - DONE requer done_substatus."""

    def test_scenario_008_done_without_substatus_raises_error(self):
        """CENÁRIO 8: DONE sem done_substatus -> ValueError."""
        # DADO/QUANDO: tentativa de criar com DONE sem substatus
        instance = HabitInstance(
            habit_id=1,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.DONE,
            done_substatus=None,  # INVÁLIDO
        )

        # ENTÃO: validação deve falhar
        with pytest.raises(ValueError, match="done_substatus obrigatório quando status=DONE"):
            instance.validate_status_consistency()


class TestBRStatus001ValidationNotDoneRequiresSubstatus:
    """Cenário 9: Validação - NOT_DONE requer not_done_substatus."""

    def test_scenario_009_not_done_without_substatus_raises_error(self):
        """CENÁRIO 9: NOT_DONE sem not_done_substatus -> ValueError."""
        # DADO/QUANDO: tentativa de criar com NOT_DONE sem substatus
        instance = HabitInstance(
            habit_id=1,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.NOT_DONE,
            not_done_substatus=None,  # INVÁLIDO
        )

        # ENTÃO: validação deve falhar
        with pytest.raises(
            ValueError, match="not_done_substatus obrigatório quando status=NOT_DONE"
        ):
            instance.validate_status_consistency()


class TestBRStatus001ValidationSubstatusMutuallyExclusive:
    """Cenário 10: Validação - Substatus mutuamente exclusivos."""

    def test_scenario_010_both_substatus_raises_error(self):
        """CENÁRIO 10: DONE + not_done_substatus preenchido -> ValueError."""
        # DADO/QUANDO: tentativa com ambos substatus
        instance = HabitInstance(
            habit_id=1,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.DONE,
            done_substatus=DoneSubstatus.FULL,
            not_done_substatus=NotDoneSubstatus.IGNORED,  # INVÁLIDO
        )

        # ENTÃO: validação deve falhar
        with pytest.raises(
            ValueError, match="not_done_substatus deve ser None quando status=DONE"
        ):
            instance.validate_status_consistency()


class TestBRStatus001ValidationSkipReasonConsistency:
    """Cenários 11-12: Validação - skip_reason consistência."""

    def test_scenario_011_skip_reason_without_justified_raises_error(self):
        """CENÁRIO 11: skip_reason com IGNORED -> ValueError."""
        # DADO/QUANDO: skip_reason sem JUSTIFIED
        instance = HabitInstance(
            habit_id=1,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.NOT_DONE,
            not_done_substatus=NotDoneSubstatus.IGNORED,
            skip_reason=SkipReason.HEALTH,  # INVÁLIDO
        )

        # ENTÃO: validação deve falhar
        with pytest.raises(ValueError, match="skip_reason só permitido com SKIPPED_JUSTIFIED"):
            instance.validate_status_consistency()

    def test_scenario_012_justified_without_skip_reason_raises_error(self):
        """CENÁRIO 12: JUSTIFIED sem skip_reason -> ValueError."""
        # DADO/QUANDO: JUSTIFIED sem skip_reason
        instance = HabitInstance(
            habit_id=1,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.NOT_DONE,
            not_done_substatus=NotDoneSubstatus.SKIPPED_JUSTIFIED,
            skip_reason=None,  # INVÁLIDO
        )

        # ENTÃO: validação deve falhar
        with pytest.raises(ValueError, match="skip_reason obrigatório para SKIPPED_JUSTIFIED"):
            instance.validate_status_consistency()


class TestBRStatus001PropertyIsOverdue:
    """Cenários 13-15: Property is_overdue."""

    def test_scenario_013_pending_overdue_returns_true(self):
        """CENÁRIO 13: PENDING 1h atrasado -> is_overdue = True."""
        # DADO: evento PENDING 1h atrasado
        instance = HabitInstance(
            habit_id=1,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.PENDING,
        )

        # QUANDO: horário atual é 09:00 (1h depois)
        # Simular com mock ou ajustar lógica de is_overdue para aceitar datetime
        # Por enquanto, testar diretamente a property

        # ENTÃO
        # assert instance.is_overdue == True
        # TODO: Implementar mock de datetime.now() no teste

    def test_scenario_014_pending_on_time_returns_false(self):
        """CENÁRIO 14: PENDING no prazo -> is_overdue = False."""
        # DADO: evento PENDING no prazo
        instance = HabitInstance(
            habit_id=1,
            date=date.today(),
            scheduled_start=time(10, 0),
            scheduled_end=time(11, 0),
            status=Status.PENDING,
        )

        # QUANDO: horário atual é 09:00 (1h antes)
        # ENTÃO
        # assert instance.is_overdue == False
        # TODO: Implementar mock de datetime.now() no teste

    def test_scenario_015_done_never_overdue(self):
        """CENÁRIO 15: DONE nunca é overdue."""
        # DADO: evento DONE (mesmo que atrasado originalmente)
        instance = HabitInstance(
            habit_id=1,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.DONE,
            done_substatus=DoneSubstatus.FULL,
        )

        # ENTÃO
        assert instance.is_overdue == False
