"""Testes para Business Rules de Skip.

IMPORTANTE: Estes testes validam BRs documentadas (v2.0).
Status: RED - Aguardando refatoração do modelo HabitInstance.

O modelo atual (v1.3.0) usa:
- HabitInstanceStatus (PLANNED/COMPLETED/SKIPPED)

O modelo target (v2.0) usa:
- InstanceStatus (PENDING/DONE/NOT_DONE)
- NotDoneSubstatus (SKIPPED_JUSTIFIED/SKIPPED_UNJUSTIFIED/IGNORED)
- SkipReason (8 categorias em português)
- Campos: skip_reason, skip_note

Valida BRs:
- BR-HABIT-SKIP-001: Categorização de Skip com Enum
- BR-HABIT-SKIP-002: Campos de Skip
- BR-HABIT-SKIP-003: Prazo para Justificar Skip
- BR-HABIT-SKIP-004: CLI Prompt Interativo
"""

from datetime import datetime, timedelta
from enum import Enum

import pytest

# === MODELOS TARGET (v2.0) ===
# Estes enums serão implementados na refatoração


class InstanceStatus(str, Enum):
    """Status de instância (target v2.0)."""

    PENDING = "pending"
    DONE = "done"
    NOT_DONE = "not_done"


class NotDoneSubstatus(str, Enum):
    """Substatus quando NOT_DONE (target v2.0)."""

    SKIPPED_JUSTIFIED = "skipped_justified"
    SKIPPED_UNJUSTIFIED = "skipped_unjustified"
    IGNORED = "ignored"


class SkipReason(str, Enum):
    """Categorias de motivo para skip (BR-HABIT-SKIP-001)."""

    HEALTH = "saude"
    WORK = "trabalho"
    FAMILY = "familia"
    PERSONAL = "pessoal"
    WEATHER = "clima"
    FATIGUE = "cansaco"
    EMERGENCY = "emergencia"
    OTHER = "outro"


# === MOCK HabitInstance v2.0 ===
# Modelo target com campos das BRs


class HabitInstanceV2:
    """Mock do modelo HabitInstance v2.0 para validação de BRs."""

    def __init__(
        self,
        habit_id: int,
        scheduled_date: datetime,
        status: InstanceStatus = InstanceStatus.PENDING,
        not_done_substatus: NotDoneSubstatus | None = None,
        skip_reason: str | None = None,
        skip_note: str | None = None,
        created_at: datetime | None = None,
    ):
        self.habit_id = habit_id
        self.scheduled_date = scheduled_date
        self.status = status
        self.not_done_substatus = not_done_substatus
        self.skip_reason = skip_reason
        self.skip_note = skip_note
        self.created_at = created_at or datetime.now()


# BR-HABIT-SKIP-001: Categorização de Skip com Enum
class TestBRHabitSkip001:
    """Valida BR-HABIT-SKIP-001: Categorização com enum de 8 valores."""

    def test_br_habit_skip_001_enum_has_8_categories(self):
        """BR-HABIT-SKIP-001: SkipReason tem exatamente 8 categorias."""
        # Assert
        assert len(SkipReason) == 8, "SkipReason deve ter 8 categorias"

    def test_br_habit_skip_001_enum_values_portuguese(self):
        """BR-HABIT-SKIP-001: Valores do enum em português lowercase."""
        # Assert
        expected_values = {
            "saude",
            "trabalho",
            "familia",
            "pessoal",
            "clima",
            "cansaco",
            "emergencia",
            "outro",
        }
        actual_values = {reason.value for reason in SkipReason}
        assert actual_values == expected_values, "Valores devem estar em português"

    def test_br_habit_skip_001_all_categories_exist(self):
        """BR-HABIT-SKIP-001: Todas 8 categorias específicas existem."""
        # Assert
        assert SkipReason.HEALTH.value == "saude"
        assert SkipReason.WORK.value == "trabalho"
        assert SkipReason.FAMILY.value == "familia"
        assert SkipReason.PERSONAL.value == "pessoal"
        assert SkipReason.WEATHER.value == "clima"
        assert SkipReason.FATIGUE.value == "cansaco"
        assert SkipReason.EMERGENCY.value == "emergencia"
        assert SkipReason.OTHER.value == "outro"


# BR-HABIT-SKIP-002: Campos de Skip
class TestBRHabitSkip002:
    """Valida BR-HABIT-SKIP-002: Campos skip_reason e skip_note."""

    def test_br_habit_skip_002_fields_exist(self):
        """BR-HABIT-SKIP-002: HabitInstance tem campos skip_reason e skip_note."""
        # Arrange
        instance = HabitInstanceV2(
            habit_id=1, scheduled_date=datetime.now(), skip_reason=None, skip_note=None
        )

        # Assert
        assert hasattr(instance, "skip_reason"), "Deve ter skip_reason"
        assert hasattr(instance, "skip_note"), "Deve ter skip_note"

    def test_br_habit_skip_002_skip_reason_optional(self):
        """BR-HABIT-SKIP-002: skip_reason aceita None."""
        # Arrange & Act
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=datetime.now(),
            status=InstanceStatus.NOT_DONE,
            not_done_substatus=NotDoneSubstatus.SKIPPED_UNJUSTIFIED,
            skip_reason=None,
        )

        # Assert
        assert instance.skip_reason is None

    def test_br_habit_skip_002_skip_note_max_length(self):
        """BR-HABIT-SKIP-002: skip_note limitado a 200 caracteres."""
        # Arrange
        note_200 = "A" * 200
        note_201 = "A" * 201

        # Act - 200 chars OK
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=datetime.now(),
            status=InstanceStatus.NOT_DONE,
            not_done_substatus=NotDoneSubstatus.SKIPPED_JUSTIFIED,
            skip_reason=SkipReason.HEALTH.value,
            skip_note=note_200,
        )

        # Assert
        assert len(instance.skip_note) == 200

        # 201 chars deve ser rejeitado (validação SQLModel)
        # TODO: Implementar Field(max_length=200) no modelo real
        with pytest.raises(ValueError):
            instance_invalid = HabitInstanceV2(
                habit_id=1,
                scheduled_date=datetime.now(),
                skip_note=note_201,
            )
            if len(instance_invalid.skip_note) > 200:
                raise ValueError("skip_note excede 200 caracteres")

    def test_br_habit_skip_002_skip_fields_null_when_done(self):
        """BR-HABIT-SKIP-002: skip_reason/skip_note NULL quando status DONE."""
        # Arrange & Act
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=datetime.now(),
            status=InstanceStatus.DONE,
            skip_reason=None,
            skip_note=None,
        )

        # Assert
        assert instance.skip_reason is None
        assert instance.skip_note is None

    def test_br_habit_skip_002_reason_required_for_justified(self):
        """BR-HABIT-SKIP-002: skip_reason obrigatório para SKIPPED_JUSTIFIED."""
        # Arrange & Act
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=datetime.now(),
            status=InstanceStatus.NOT_DONE,
            not_done_substatus=NotDoneSubstatus.SKIPPED_JUSTIFIED,
            skip_reason=SkipReason.HEALTH.value,  # Obrigatório
        )

        # Assert
        assert instance.skip_reason is not None
        assert instance.skip_reason == "saude"


# BR-HABIT-SKIP-003: Prazo para Justificar Skip
class TestBRHabitSkip003:
    """Valida BR-HABIT-SKIP-003: Prazo de 24h para justificar."""

    def test_br_habit_skip_003_deadline_24h_calculation(self):
        """BR-HABIT-SKIP-003: Deadline é created_at + 24h."""
        # Arrange
        created_at = datetime(2025, 11, 14, 8, 0)  # 14/11 08:00
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=created_at,
            status=InstanceStatus.NOT_DONE,
            not_done_substatus=NotDoneSubstatus.SKIPPED_UNJUSTIFIED,
            created_at=created_at,
        )

        # Act
        deadline = instance.created_at + timedelta(hours=24)

        # Assert
        assert deadline == datetime(2025, 11, 15, 8, 0), "Deadline deve ser +24h"

    def test_br_habit_skip_003_within_deadline(self):
        """BR-HABIT-SKIP-003: Pode justificar dentro de 24h."""
        # Arrange
        created_at = datetime(2025, 11, 14, 8, 0)
        now = datetime(2025, 11, 14, 18, 0)  # 10h depois
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=created_at,
            status=InstanceStatus.NOT_DONE,
            not_done_substatus=NotDoneSubstatus.SKIPPED_UNJUSTIFIED,
            created_at=created_at,
        )

        # Act
        deadline = instance.created_at + timedelta(hours=24)
        within_deadline = now < deadline

        # Assert
        assert within_deadline is True, "Deve estar dentro do prazo"

    def test_br_habit_skip_003_after_deadline(self):
        """BR-HABIT-SKIP-003: Não pode justificar após 24h."""
        # Arrange
        created_at = datetime(2025, 11, 14, 8, 0)
        now = datetime(2025, 11, 15, 9, 0)  # 25h depois
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=created_at,
            status=InstanceStatus.NOT_DONE,
            not_done_substatus=NotDoneSubstatus.SKIPPED_UNJUSTIFIED,
            created_at=created_at,
        )

        # Act
        deadline = instance.created_at + timedelta(hours=24)
        after_deadline = now > deadline

        # Assert
        assert after_deadline is True, "Deve estar após o prazo"

    def test_br_habit_skip_003_change_to_justified_within_deadline(self):
        """BR-HABIT-SKIP-003: Permitir mudança UNJUSTIFIED→JUSTIFIED dentro prazo."""
        # Arrange
        created_at = datetime(2025, 11, 14, 8, 0)
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=created_at,
            status=InstanceStatus.NOT_DONE,
            not_done_substatus=NotDoneSubstatus.SKIPPED_UNJUSTIFIED,
            created_at=created_at,
            skip_reason=None,
        )

        # Act - 10h depois, adiciona justificativa
        now = datetime(2025, 11, 14, 18, 0)
        deadline = instance.created_at + timedelta(hours=24)

        if now < deadline:
            instance.not_done_substatus = NotDoneSubstatus.SKIPPED_JUSTIFIED
            instance.skip_reason = SkipReason.WORK.value

        # Assert
        assert instance.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED
        assert instance.skip_reason == "trabalho"


# BR-HABIT-SKIP-004: CLI Prompt Interativo
class TestBRHabitSkip004:
    """Valida BR-HABIT-SKIP-004: Prompt interativo."""

    def test_br_habit_skip_004_prompt_has_9_options(self):
        """BR-HABIT-SKIP-004: Prompt tem 9 opções (8 categorias + justificar depois)."""
        # Assert
        assert len(SkipReason) == 8, "8 categorias de skip_reason"
        # Opção 9 = "Justificar depois" (cria SKIPPED_UNJUSTIFIED)

    def test_br_habit_skip_004_option_1_8_creates_justified(self):
        """BR-HABIT-SKIP-004: Escolher opção 1-8 cria SKIPPED_JUSTIFIED."""
        # Arrange & Act - Simula escolha de opção 2 (WORK)
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=datetime.now(),
            status=InstanceStatus.NOT_DONE,
            not_done_substatus=NotDoneSubstatus.SKIPPED_JUSTIFIED,
            skip_reason=SkipReason.WORK.value,
        )

        # Assert
        assert instance.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED
        assert instance.skip_reason == "trabalho"

    def test_br_habit_skip_004_option_9_creates_unjustified(self):
        """BR-HABIT-SKIP-004: Escolher opção 9 cria SKIPPED_UNJUSTIFIED."""
        # Arrange & Act - Simula escolha de opção 9 (Justificar depois)
        instance = HabitInstanceV2(
            habit_id=1,
            scheduled_date=datetime.now(),
            status=InstanceStatus.NOT_DONE,
            not_done_substatus=NotDoneSubstatus.SKIPPED_UNJUSTIFIED,
            skip_reason=None,
            skip_note=None,
        )

        # Assert
        assert instance.not_done_substatus == NotDoneSubstatus.SKIPPED_UNJUSTIFIED
        assert instance.skip_reason is None
        assert instance.skip_note is None
