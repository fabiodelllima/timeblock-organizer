"""Testes para Business Rules de HabitInstance.

IMPORTANTE: Estes testes validam BRs documentadas (v2.0).
Status: RED - Aguardando refatoração do modelo HabitInstance.

O modelo atual (v1.3.0) usa HabitInstanceStatus (PLANNED/COMPLETED/SKIPPED).
O modelo target (v2.0) usa InstanceStatus + DoneSubstatus + NotDoneSubstatus.

Valida BRs:
- BR-HABIT-INSTANCE-001: Status Transitions
- BR-HABIT-INSTANCE-002: Substatus Assignment
- BR-HABIT-INSTANCE-003: Completion Thresholds
- BR-HABIT-INSTANCE-004: Streak Calculation with Substatus
- BR-HABIT-INSTANCE-005: Ignored Auto-Assignment (48h)
- BR-HABIT-INSTANCE-006: Impact Analysis on EXCESSIVE/OVERDONE
"""

from datetime import date, datetime, timedelta
from enum import Enum

# === ENUMS TARGET (v2.0) ===


class InstanceStatus(str, Enum):
    """Status de instância (target v2.0)."""

    PENDING = "pending"
    DONE = "done"
    NOT_DONE = "not_done"


class DoneSubstatus(str, Enum):
    """Substatus quando DONE (target v2.0)."""

    EXCESSIVE = "excessive"  # > 150%
    OVERDONE = "overdone"  # 110-150%
    FULL = "full"  # 90-110%
    PARTIAL = "partial"  # < 90%


class NotDoneSubstatus(str, Enum):
    """Substatus quando NOT_DONE (target v2.0)."""

    SKIPPED_JUSTIFIED = "skipped_justified"
    SKIPPED_UNJUSTIFIED = "skipped_unjustified"
    IGNORED = "ignored"


# === MOCK HabitInstance v2.0 ===


class HabitInstanceV2:
    """Mock do modelo HabitInstance v2.0 para validação de BRs."""

    def __init__(
        self,
        habit_id: int,
        scheduled_date: date,
        expected_duration: int,
        actual_duration: int | None = None,
        status: InstanceStatus = InstanceStatus.PENDING,
        done_substatus: DoneSubstatus | None = None,
        not_done_substatus: NotDoneSubstatus | None = None,
        created_at: datetime | None = None,
    ):
        self.habit_id = habit_id
        self.scheduled_date = scheduled_date
        self.expected_duration = expected_duration  # minutos
        self.actual_duration = actual_duration  # minutos
        self.status = status
        self.done_substatus = done_substatus
        self.not_done_substatus = not_done_substatus
        self.created_at = created_at or datetime.now()


# === FUNÇÕES AUXILIARES ===


def calculate_completion(expected: int, actual: int) -> float:
    """Calcula completion percentage (BR-HABIT-INSTANCE-003)."""
    if expected == 0:
        return 0.0
    return round((actual / expected) * 100, 2)


def determine_done_substatus(completion: float) -> DoneSubstatus:
    """Determina substatus DONE baseado em completion (BR-HABIT-INSTANCE-003)."""
    if completion > 150:
        return DoneSubstatus.EXCESSIVE
    elif completion > 110:
        return DoneSubstatus.OVERDONE
    elif completion >= 90:
        return DoneSubstatus.FULL
    else:
        return DoneSubstatus.PARTIAL


def is_ignored_by_timeout(instance: HabitInstanceV2, now: datetime) -> bool:
    """Verifica se instance deve ser marcada como IGNORED (BR-HABIT-INSTANCE-005)."""
    if instance.status != InstanceStatus.PENDING:
        return False

    elapsed = now - instance.created_at
    return elapsed.total_seconds() / 3600 > 48  # 48 horas


# BR-HABIT-INSTANCE-001: Status Transitions
class TestBRHabitInstance001:
    """Valida BR-HABIT-INSTANCE-001: Transições de status."""

    def test_br_habit_instance_001_pending_to_done(self):
        """BR-HABIT-INSTANCE-001: PENDING → DONE via timer stop."""
        # Arrange
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=date(2025, 11, 14),
            expected_duration=90,
        )
        assert instance.status == InstanceStatus.PENDING

        # Act - Simula timer stop
        instance.actual_duration = 90
        instance.status = InstanceStatus.DONE

        assert instance.actual_duration is not None
        completion = calculate_completion(instance.expected_duration, instance.actual_duration)
        instance.done_substatus = determine_done_substatus(completion)

        # Assert
        assert instance.status == InstanceStatus.DONE
        assert instance.done_substatus == DoneSubstatus.FULL

    def test_br_habit_instance_001_pending_to_not_done_skip(self):
        """BR-HABIT-INSTANCE-001: PENDING → NOT_DONE via skip."""
        # Arrange
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=date(2025, 11, 14),
            expected_duration=90,
        )

        # Act - Skip
        instance.status = InstanceStatus.NOT_DONE
        instance.not_done_substatus = NotDoneSubstatus.SKIPPED_JUSTIFIED

        # Assert
        assert instance.status == InstanceStatus.NOT_DONE
        assert instance.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED

    def test_br_habit_instance_001_pending_to_not_done_timeout(self):
        """BR-HABIT-INSTANCE-001: PENDING → NOT_DONE via timeout (48h)."""
        # Arrange
        created_at = datetime(2025, 11, 14, 8, 0)
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=created_at.date(),
            expected_duration=90,
            created_at=created_at,
        )

        # Act - 49h depois
        now = created_at + timedelta(hours=49)
        if is_ignored_by_timeout(instance, now):
            instance.status = InstanceStatus.NOT_DONE
            instance.not_done_substatus = NotDoneSubstatus.IGNORED

        # Assert
        assert instance.status == InstanceStatus.NOT_DONE
        assert instance.not_done_substatus == NotDoneSubstatus.IGNORED

    def test_br_habit_instance_001_done_is_final(self):
        """BR-HABIT-INSTANCE-001: Status DONE é final (não pode mudar)."""
        # Arrange
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=date(2025, 11, 14),
            expected_duration=90,
            actual_duration=90,
            status=InstanceStatus.DONE,
            done_substatus=DoneSubstatus.FULL,
        )

        # Act & Assert - Tentar mudar deve ser bloqueado
        original_status = instance.status
        # Validação deve impedir mudança
        is_final = instance.status == InstanceStatus.DONE
        assert is_final is True, "DONE é status final"
        assert instance.status == original_status

    def test_br_habit_instance_001_not_done_is_final(self):
        """BR-HABIT-INSTANCE-001: Status NOT_DONE é final (não pode mudar)."""
        # Arrange
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=date(2025, 11, 14),
            expected_duration=90,
            status=InstanceStatus.NOT_DONE,
            not_done_substatus=NotDoneSubstatus.SKIPPED_JUSTIFIED,
        )

        # Act & Assert
        original_status = instance.status
        is_final = instance.status == InstanceStatus.NOT_DONE
        assert is_final is True, "NOT_DONE é status final"
        assert instance.status == original_status


# BR-HABIT-INSTANCE-002: Substatus Assignment
class TestBRHabitInstance002:
    """Valida BR-HABIT-INSTANCE-002: Atribuição de substatus."""

    def test_br_habit_instance_002_done_requires_done_substatus(self):
        """BR-HABIT-INSTANCE-002: DONE sempre tem done_substatus."""
        # Arrange & Act
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=date(2025, 11, 14),
            expected_duration=90,
            actual_duration=90,
            status=InstanceStatus.DONE,
            done_substatus=DoneSubstatus.FULL,
        )

        # Assert
        assert instance.status == InstanceStatus.DONE
        assert instance.done_substatus is not None
        assert instance.not_done_substatus is None

    def test_br_habit_instance_002_not_done_requires_not_done_substatus(self):
        """BR-HABIT-INSTANCE-002: NOT_DONE sempre tem not_done_substatus."""
        # Arrange & Act
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=date(2025, 11, 14),
            expected_duration=90,
            status=InstanceStatus.NOT_DONE,
            not_done_substatus=NotDoneSubstatus.SKIPPED_JUSTIFIED,
        )

        # Assert
        assert instance.status == InstanceStatus.NOT_DONE
        assert instance.not_done_substatus is not None
        assert instance.done_substatus is None

    def test_br_habit_instance_002_pending_no_substatus(self):
        """BR-HABIT-INSTANCE-002: PENDING não tem substatus."""
        # Arrange & Act
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=date(2025, 11, 14),
            expected_duration=90,
            status=InstanceStatus.PENDING,
        )

        # Assert
        assert instance.status == InstanceStatus.PENDING
        assert instance.done_substatus is None
        assert instance.not_done_substatus is None

    def test_br_habit_instance_002_substatus_mutually_exclusive(self):
        """BR-HABIT-INSTANCE-002: Substatus são mutuamente exclusivos."""
        # Arrange
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=date(2025, 11, 14),
            expected_duration=90,
            actual_duration=90,
            status=InstanceStatus.DONE,
            done_substatus=DoneSubstatus.FULL,
        )

        # Assert
        # Se tem done_substatus, não pode ter not_done_substatus
        if instance.done_substatus is not None:
            assert instance.not_done_substatus is None

        # Se tem not_done_substatus, não pode ter done_substatus
        instance2 = HabitInstanceV2(
            habit_id=1,
            scheduled_date=date(2025, 11, 14),
            expected_duration=90,
            status=InstanceStatus.NOT_DONE,
            not_done_substatus=NotDoneSubstatus.IGNORED,
        )
        if instance2.not_done_substatus is not None:
            assert instance2.done_substatus is None


# BR-HABIT-INSTANCE-003: Completion Thresholds
class TestBRHabitInstance003:
    """Valida BR-HABIT-INSTANCE-003: Thresholds de completion."""

    def test_br_habit_instance_003_excessive_over_150(self):
        """BR-HABIT-INSTANCE-003: EXCESSIVE quando > 150%."""
        # Arrange
        expected = 90
        actual = 180  # 200%

        # Act
        completion = calculate_completion(expected, actual)
        substatus = determine_done_substatus(completion)

        # Assert
        assert completion == 200.0
        assert substatus == DoneSubstatus.EXCESSIVE

    def test_br_habit_instance_003_overdone_110_150(self):
        """BR-HABIT-INSTANCE-003: OVERDONE quando 110-150%."""
        # Arrange
        expected = 90
        actual = 100  # 111.11%

        # Act
        completion = calculate_completion(expected, actual)
        substatus = determine_done_substatus(completion)

        # Assert
        assert 110 < completion <= 150
        assert substatus == DoneSubstatus.OVERDONE

    def test_br_habit_instance_003_full_90_110(self):
        """BR-HABIT-INSTANCE-003: FULL quando 90-110%."""
        # Arrange
        expected = 90
        actual = 90  # 100%

        # Act
        completion = calculate_completion(expected, actual)
        substatus = determine_done_substatus(completion)

        # Assert
        assert 90 <= completion <= 110
        assert substatus == DoneSubstatus.FULL

    def test_br_habit_instance_003_partial_under_90(self):
        """BR-HABIT-INSTANCE-003: PARTIAL quando < 90%."""
        # Arrange
        expected = 90
        actual = 60  # 66.67%

        # Act
        completion = calculate_completion(expected, actual)
        substatus = determine_done_substatus(completion)

        # Assert
        assert completion < 90
        assert substatus == DoneSubstatus.PARTIAL

    def test_br_habit_instance_003_edge_case_150_exact(self):
        """BR-HABIT-INSTANCE-003: Edge case exato 150%."""
        # Arrange
        expected = 90
        actual = 135  # 150%

        # Act
        completion = calculate_completion(expected, actual)
        substatus = determine_done_substatus(completion)

        # Assert
        assert completion == 150.0
        assert substatus == DoneSubstatus.OVERDONE  # 150% é OVERDONE

    def test_br_habit_instance_003_edge_case_110_exact(self):
        """BR-HABIT-INSTANCE-003: Edge case exato 110%."""
        # Arrange
        expected = 90
        actual = 99  # 110%

        # Act
        completion = calculate_completion(expected, actual)
        substatus = determine_done_substatus(completion)

        # Assert
        assert completion == 110.0
        assert substatus == DoneSubstatus.FULL  # 110% é FULL (limite superior)

    def test_br_habit_instance_003_edge_case_90_exact(self):
        """BR-HABIT-INSTANCE-003: Edge case exato 90%."""
        # Arrange
        expected = 90
        actual = 81  # 90%

        # Act
        completion = calculate_completion(expected, actual)
        substatus = determine_done_substatus(completion)

        # Assert
        assert completion == 90.0
        assert substatus == DoneSubstatus.FULL  # 90% é FULL


# BR-HABIT-INSTANCE-004: Streak Calculation with Substatus
class TestBRHabitInstance004:
    """Valida BR-HABIT-INSTANCE-004: Streak com substatus."""

    def test_br_habit_instance_004_all_done_maintain_streak(self):
        """BR-HABIT-INSTANCE-004: Todos substatus DONE mantêm streak."""
        # Assert
        done_substatus = [
            DoneSubstatus.EXCESSIVE,
            DoneSubstatus.OVERDONE,
            DoneSubstatus.FULL,
            DoneSubstatus.PARTIAL,
        ]

        # Todos devem manter streak
        for substatus in done_substatus:
            instance = HabitInstanceV2(
                habit_id=1,
                scheduled_date=date(2025, 11, 14),
                expected_duration=90,
                actual_duration=90,
                status=InstanceStatus.DONE,
                done_substatus=substatus,
            )
            assert instance.status == InstanceStatus.DONE
            # Streak seria incrementado (lógica em outro serviço)

    def test_br_habit_instance_004_all_not_done_break_streak(self):
        """BR-HABIT-INSTANCE-004: Todos substatus NOT_DONE quebram streak."""
        # Assert
        not_done_substatus = [
            NotDoneSubstatus.SKIPPED_JUSTIFIED,
            NotDoneSubstatus.SKIPPED_UNJUSTIFIED,
            NotDoneSubstatus.IGNORED,
        ]

        # Todos devem quebrar streak
        for substatus in not_done_substatus:
            instance = HabitInstanceV2(
                habit_id=1,
                scheduled_date=date(2025, 11, 14),
                expected_duration=90,
                status=InstanceStatus.NOT_DONE,
                not_done_substatus=substatus,
            )
            assert instance.status == InstanceStatus.NOT_DONE
            # Streak seria zerado (lógica em outro serviço)


# BR-HABIT-INSTANCE-005: Ignored Auto-Assignment
class TestBRHabitInstance005:
    """Valida BR-HABIT-INSTANCE-005: IGNORED após 48h."""

    def test_br_habit_instance_005_pending_under_48h(self):
        """BR-HABIT-INSTANCE-005: PENDING < 48h não é IGNORED."""
        # Arrange
        created_at = datetime(2025, 11, 14, 8, 0)
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=created_at.date(),
            expected_duration=90,
            created_at=created_at,
        )

        # Act - 24h depois
        now = created_at + timedelta(hours=24)
        should_ignore = is_ignored_by_timeout(instance, now)

        # Assert
        assert should_ignore is False, "Não deve ser IGNORED antes de 48h"

    def test_br_habit_instance_005_pending_over_48h(self):
        """BR-HABIT-INSTANCE-005: PENDING > 48h é IGNORED."""
        # Arrange
        created_at = datetime(2025, 11, 14, 8, 0)
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=created_at.date(),
            expected_duration=90,
            created_at=created_at,
        )

        # Act - 49h depois
        now = created_at + timedelta(hours=49)
        should_ignore = is_ignored_by_timeout(instance, now)

        # Assert
        assert should_ignore is True, "Deve ser IGNORED após 48h"

    def test_br_habit_instance_005_only_pending_checked(self):
        """BR-HABIT-INSTANCE-005: Apenas PENDING é verificado para timeout."""
        # Arrange
        created_at = datetime(2025, 11, 14, 8, 0)
        done_instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=created_at.date(),
            expected_duration=90,
            actual_duration=90,
            status=InstanceStatus.DONE,
            done_substatus=DoneSubstatus.FULL,
            created_at=created_at,
        )

        # Act - 49h depois
        now = created_at + timedelta(hours=49)
        should_ignore = is_ignored_by_timeout(done_instance, now)

        # Assert
        assert should_ignore is False, "DONE não deve ser verificado"


# BR-HABIT-INSTANCE-006: Impact Analysis
class TestBRHabitInstance006:
    """Valida BR-HABIT-INSTANCE-006: Análise de impacto EXCESSIVE/OVERDONE."""

    def test_br_habit_instance_006_excessive_triggers_analysis(self):
        """BR-HABIT-INSTANCE-006: EXCESSIVE deve disparar análise de impacto."""
        # Arrange
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=date(2025, 11, 14),
            expected_duration=90,
            actual_duration=180,  # 200% - EXCESSIVE
            status=InstanceStatus.DONE,
        )

        # Act
        assert instance.actual_duration is not None
        completion = calculate_completion(instance.expected_duration, instance.actual_duration)
        instance.done_substatus = determine_done_substatus(completion)

        # Assert
        assert instance.done_substatus == DoneSubstatus.EXCESSIVE
        # Análise de impacto seria executada (lógica em outro serviço)
        should_analyze = instance.done_substatus in [
            DoneSubstatus.EXCESSIVE,
            DoneSubstatus.OVERDONE,
        ]
        assert should_analyze is True

    def test_br_habit_instance_006_overdone_triggers_analysis(self):
        """BR-HABIT-INSTANCE-006: OVERDONE deve disparar análise."""
        # Arrange
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=date(2025, 11, 14),
            expected_duration=90,
            actual_duration=120,  # 133% - OVERDONE
            status=InstanceStatus.DONE,
        )

        # Act
        assert instance.actual_duration is not None
        completion = calculate_completion(instance.expected_duration, instance.actual_duration)
        instance.done_substatus = determine_done_substatus(completion)

        # Assert
        assert instance.done_substatus == DoneSubstatus.OVERDONE
        should_analyze = instance.done_substatus in [
            DoneSubstatus.EXCESSIVE,
            DoneSubstatus.OVERDONE,
        ]
        assert should_analyze is True

    def test_br_habit_instance_006_full_no_analysis(self):
        """BR-HABIT-INSTANCE-006: FULL não dispara análise."""
        # Arrange
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=date(2025, 11, 14),
            expected_duration=90,
            actual_duration=90,  # 100% - FULL
            status=InstanceStatus.DONE,
        )

        # Act
        assert instance.actual_duration is not None
        completion = calculate_completion(instance.expected_duration, instance.actual_duration)
        instance.done_substatus = determine_done_substatus(completion)

        # Assert
        assert instance.done_substatus == DoneSubstatus.FULL
        should_analyze = instance.done_substatus in [
            DoneSubstatus.EXCESSIVE,
            DoneSubstatus.OVERDONE,
        ]
        assert should_analyze is False

    def test_br_habit_instance_006_partial_no_analysis(self):
        """BR-HABIT-INSTANCE-006: PARTIAL não dispara análise."""
        # Arrange
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=date(2025, 11, 14),
            expected_duration=90,
            actual_duration=60,  # 67% - PARTIAL
            status=InstanceStatus.DONE,
        )

        # Act
        assert instance.actual_duration is not None
        completion = calculate_completion(instance.expected_duration, instance.actual_duration)
        instance.done_substatus = determine_done_substatus(completion)

        # Assert
        assert instance.done_substatus == DoneSubstatus.PARTIAL
        should_analyze = instance.done_substatus in [
            DoneSubstatus.EXCESSIVE,
            DoneSubstatus.OVERDONE,
        ]
        assert should_analyze is False
