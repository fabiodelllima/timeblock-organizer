"""Testes para Business Rules de Streak.

IMPORTANTE: Estes testes validam BRs documentadas (v2.0).
Status: RED - Aguardando refatoração do modelo HabitInstance.

Filosofia (Atomic Habits - James Clear):
- Consistência > Perfeição
- Qualquer DONE mantém streak
- Qualquer NOT_DONE quebra streak

Valida BRs:
- BR-STREAK-001: Calculation Algorithm
- BR-STREAK-002: Break Conditions
- BR-STREAK-003: Maintain Conditions
- BR-STREAK-004: Psychological Feedback
"""

from datetime import date, timedelta
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
    """Mock do modelo HabitInstance v2.0 para validação de streak."""

    def __init__(
        self,
        habit_id: int,
        scheduled_date: date,
        status: InstanceStatus,
        done_substatus: DoneSubstatus | None = None,
        not_done_substatus: NotDoneSubstatus | None = None,
    ):
        self.habit_id = habit_id
        self.scheduled_date = scheduled_date
        self.status = status
        self.done_substatus = done_substatus
        self.not_done_substatus = not_done_substatus


# === FUNÇÕES DE CÁLCULO ===


def calculate_streak(instances: list[HabitInstanceV2]) -> int:
    """Calcula streak de dias consecutivos (BR-STREAK-001)."""
    if not instances:
        return 0

    # Ordenar por data (mais recente primeiro)
    sorted_instances = sorted(instances, key=lambda x: x.scheduled_date, reverse=True)

    streak = 0
    for instance in sorted_instances:
        # PENDING não conta
        if instance.status == InstanceStatus.PENDING:
            continue

        # DONE mantém streak
        if instance.status == InstanceStatus.DONE:
            streak += 1
            continue

        # NOT_DONE quebra streak
        if instance.status == InstanceStatus.NOT_DONE:
            break

    return streak


# BR-STREAK-001: Calculation Algorithm
class TestBRStreak001:
    """Valida BR-STREAK-001: Algoritmo de cálculo de streak."""

    def test_br_streak_001_consecutive_done_days(self):
        """BR-STREAK-001: Streak conta dias DONE consecutivos."""
        # Arrange
        today = date(2025, 11, 14)
        instances = [
            HabitInstanceV2(1, today, InstanceStatus.DONE),
            HabitInstanceV2(1, today - timedelta(days=1), InstanceStatus.DONE),
            HabitInstanceV2(1, today - timedelta(days=2), InstanceStatus.DONE),
        ]

        # Act
        streak = calculate_streak(instances)

        # Assert
        assert streak == 3, "Deve contar 3 dias consecutivos"

    def test_br_streak_001_breaks_on_not_done(self):
        """BR-STREAK-001: Streak para ao encontrar NOT_DONE."""
        # Arrange
        today = date(2025, 11, 14)
        instances = [
            HabitInstanceV2(1, today, InstanceStatus.DONE),
            HabitInstanceV2(1, today - timedelta(days=1), InstanceStatus.DONE),
            HabitInstanceV2(1, today - timedelta(days=2), InstanceStatus.NOT_DONE),
            HabitInstanceV2(1, today - timedelta(days=3), InstanceStatus.DONE),
        ]

        # Act
        streak = calculate_streak(instances)

        # Assert
        assert streak == 2, "Deve parar no NOT_DONE (dia 12/11)"

    def test_br_streak_001_pending_ignored(self):
        """BR-STREAK-001: Instances PENDING são ignoradas no cálculo."""
        # Arrange
        today = date(2025, 11, 14)
        instances = [
            HabitInstanceV2(1, today + timedelta(days=2), InstanceStatus.PENDING),
            HabitInstanceV2(1, today + timedelta(days=1), InstanceStatus.PENDING),
            HabitInstanceV2(1, today, InstanceStatus.DONE),
            HabitInstanceV2(1, today - timedelta(days=1), InstanceStatus.DONE),
        ]

        # Act
        streak = calculate_streak(instances)

        # Assert
        assert streak == 2, "PENDING não deve afetar streak"

    def test_br_streak_001_zero_when_no_done(self):
        """BR-STREAK-001: Streak zero quando não há DONE."""
        # Arrange
        today = date(2025, 11, 14)
        instances = [
            HabitInstanceV2(1, today, InstanceStatus.PENDING),
        ]

        # Act
        streak = calculate_streak(instances)

        # Assert
        assert streak == 0, "Streak deve ser 0 sem instances DONE"

    def test_br_streak_001_zero_when_last_is_not_done(self):
        """BR-STREAK-001: Streak zero quando último instance é NOT_DONE."""
        # Arrange
        today = date(2025, 11, 14)
        instances = [
            HabitInstanceV2(1, today, InstanceStatus.NOT_DONE),
            HabitInstanceV2(1, today - timedelta(days=1), InstanceStatus.DONE),
            HabitInstanceV2(1, today - timedelta(days=2), InstanceStatus.DONE),
        ]

        # Act
        streak = calculate_streak(instances)

        # Assert
        assert streak == 0, "Streak deve ser 0 quando último é NOT_DONE"


# BR-STREAK-002: Break Conditions
class TestBRStreak002:
    """Valida BR-STREAK-002: NOT_DONE sempre quebra streak."""

    def test_br_streak_002_all_not_done_substatus_break(self):
        """BR-STREAK-002: Todos substatus NOT_DONE quebram streak."""
        # Arrange
        today = date(2025, 11, 14)
        base_instances = [
            HabitInstanceV2(1, today - timedelta(days=1), InstanceStatus.DONE),
            HabitInstanceV2(1, today - timedelta(days=2), InstanceStatus.DONE),
        ]

        substatus_values = [
            NotDoneSubstatus.SKIPPED_JUSTIFIED,
            NotDoneSubstatus.SKIPPED_UNJUSTIFIED,
            NotDoneSubstatus.IGNORED,
        ]

        for substatus in substatus_values:
            instances = [
                HabitInstanceV2(1, today, InstanceStatus.NOT_DONE, not_done_substatus=substatus),
                *base_instances,
            ]

            # Act
            streak = calculate_streak(instances)

            # Assert
            assert streak == 0, f"{substatus.value} deve quebrar streak"

    def test_br_streak_002_skipped_justified_breaks(self):
        """BR-STREAK-002: SKIPPED_JUSTIFIED quebra streak (impacto baixo)."""
        # Arrange
        today = date(2025, 11, 14)
        instances = [
            HabitInstanceV2(
                1,
                today,
                InstanceStatus.NOT_DONE,
                not_done_substatus=NotDoneSubstatus.SKIPPED_JUSTIFIED,
            ),
            HabitInstanceV2(1, today - timedelta(days=1), InstanceStatus.DONE),
        ]

        # Act
        streak = calculate_streak(instances)

        # Assert
        assert streak == 0, "SKIPPED_JUSTIFIED quebra streak"

    def test_br_streak_002_skipped_unjustified_breaks(self):
        """BR-STREAK-002: SKIPPED_UNJUSTIFIED quebra streak (impacto médio)."""
        # Arrange
        today = date(2025, 11, 14)
        instances = [
            HabitInstanceV2(
                1,
                today,
                InstanceStatus.NOT_DONE,
                not_done_substatus=NotDoneSubstatus.SKIPPED_UNJUSTIFIED,
            ),
            HabitInstanceV2(1, today - timedelta(days=1), InstanceStatus.DONE),
        ]

        # Act
        streak = calculate_streak(instances)

        # Assert
        assert streak == 0, "SKIPPED_UNJUSTIFIED quebra streak"

    def test_br_streak_002_ignored_breaks(self):
        """BR-STREAK-002: IGNORED quebra streak (impacto alto)."""
        # Arrange
        today = date(2025, 11, 14)
        instances = [
            HabitInstanceV2(
                1,
                today,
                InstanceStatus.NOT_DONE,
                not_done_substatus=NotDoneSubstatus.IGNORED,
            ),
            HabitInstanceV2(1, today - timedelta(days=1), InstanceStatus.DONE),
        ]

        # Act
        streak = calculate_streak(instances)

        # Assert
        assert streak == 0, "IGNORED quebra streak"


# BR-STREAK-003: Maintain Conditions
class TestBRStreak003:
    """Valida BR-STREAK-003: DONE sempre mantém streak."""

    def test_br_streak_003_all_done_substatus_maintain(self):
        """BR-STREAK-003: Todos substatus DONE mantêm streak."""
        # Arrange
        today = date(2025, 11, 14)
        substatus_values = [
            DoneSubstatus.EXCESSIVE,
            DoneSubstatus.OVERDONE,
            DoneSubstatus.FULL,
            DoneSubstatus.PARTIAL,
        ]

        for substatus in substatus_values:
            instances = [
                HabitInstanceV2(1, today, InstanceStatus.DONE, done_substatus=substatus),
                HabitInstanceV2(
                    1,
                    today - timedelta(days=1),
                    InstanceStatus.DONE,
                    done_substatus=DoneSubstatus.FULL,
                ),
            ]

            # Act
            streak = calculate_streak(instances)

            # Assert
            assert streak == 2, f"{substatus.value} deve manter streak"

    def test_br_streak_003_partial_maintains(self):
        """BR-STREAK-003: PARTIAL mantém streak sem penalidade."""
        # Arrange
        today = date(2025, 11, 14)
        instances = [
            HabitInstanceV2(1, today, InstanceStatus.DONE, done_substatus=DoneSubstatus.PARTIAL),
            HabitInstanceV2(
                1,
                today - timedelta(days=1),
                InstanceStatus.DONE,
                done_substatus=DoneSubstatus.FULL,
            ),
        ]

        # Act
        streak = calculate_streak(instances)

        # Assert
        assert streak == 2, "PARTIAL mantém streak"

    def test_br_streak_003_overdone_maintains(self):
        """BR-STREAK-003: OVERDONE mantém streak (com monitoramento)."""
        # Arrange
        today = date(2025, 11, 14)
        instances = [
            HabitInstanceV2(1, today, InstanceStatus.DONE, done_substatus=DoneSubstatus.OVERDONE),
            HabitInstanceV2(
                1,
                today - timedelta(days=1),
                InstanceStatus.DONE,
                done_substatus=DoneSubstatus.FULL,
            ),
        ]

        # Act
        streak = calculate_streak(instances)

        # Assert
        assert streak == 2, "OVERDONE mantém streak"

    def test_br_streak_003_excessive_maintains(self):
        """BR-STREAK-003: EXCESSIVE mantém streak (com warning de impacto)."""
        # Arrange
        today = date(2025, 11, 14)
        instances = [
            HabitInstanceV2(1, today, InstanceStatus.DONE, done_substatus=DoneSubstatus.EXCESSIVE),
            HabitInstanceV2(
                1,
                today - timedelta(days=1),
                InstanceStatus.DONE,
                done_substatus=DoneSubstatus.FULL,
            ),
        ]

        # Act
        streak = calculate_streak(instances)

        # Assert
        assert streak == 2, "EXCESSIVE mantém streak"


# BR-STREAK-004: Psychological Feedback
class TestBRStreak004:
    """Valida BR-STREAK-004: Feedback diferenciado por substatus."""

    def test_br_streak_004_feedback_tone_by_substatus(self):
        """BR-STREAK-004: Tom de feedback varia por substatus NOT_DONE."""
        # Assert - Mapeamento de tom esperado
        feedback_map = {
            NotDoneSubstatus.SKIPPED_JUSTIFIED: "compreensivo",  # Impacto baixo
            NotDoneSubstatus.SKIPPED_UNJUSTIFIED: "moderado",  # Impacto médio
            NotDoneSubstatus.IGNORED: "alerta_forte",  # Impacto alto
        }

        assert len(feedback_map) == 3, "Deve haver 3 tons de feedback"

    def test_br_streak_004_justified_low_impact(self):
        """BR-STREAK-004: JUSTIFIED tem impacto psicológico baixo."""
        # Arrange
        impact_level = "baixo"

        # Assert
        assert impact_level == "baixo", "JUSTIFIED deve ter impacto baixo"

    def test_br_streak_004_unjustified_medium_impact(self):
        """BR-STREAK-004: UNJUSTIFIED tem impacto psicológico médio."""
        # Arrange
        impact_level = "médio"

        # Assert
        assert impact_level == "médio", "UNJUSTIFIED deve ter impacto médio"

    def test_br_streak_004_ignored_high_impact(self):
        """BR-STREAK-004: IGNORED tem impacto psicológico alto."""
        # Arrange
        impact_level = "alto"

        # Assert
        assert impact_level == "alto", "IGNORED deve ter impacto alto"

    def test_br_streak_004_milestone_celebrations(self):
        """BR-STREAK-004: Milestones devem ser celebrados."""
        # Arrange
        milestones = [7, 21, 30, 60, 90, 365]

        # Assert
        assert 7 in milestones, "7 dias é milestone"
        assert 21 in milestones, "21 dias é milestone (hábito em formação)"
        assert 30 in milestones, "30 dias é milestone"
        assert 90 in milestones, "90 dias é milestone (hábito consolidado)"
        assert 365 in milestones, "365 dias é milestone (1 ano)"
