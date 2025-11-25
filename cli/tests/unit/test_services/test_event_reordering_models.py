"""Tests for event reordering models - Validação de Regras de Negócio."""

from datetime import datetime

from src.timeblock.services.event_reordering_models import Conflict, ConflictType


class TestBREvent002ConflictDataclass:
    """BR-EVENT-002: Conflict dataclass contém informações completas."""

    def test_br_event_002_conflict_com_todos_campos(self):
        """BR-EVENT-002: Conflict preserva todos os campos necessários."""
        conflict = Conflict(
            triggered_event_id=1,
            triggered_event_type="task",
            conflicting_event_id=2,
            conflicting_event_type="habit_instance",
            conflict_type=ConflictType.OVERLAP,
            triggered_start=datetime(2025, 10, 24, 10, 0),
            triggered_end=datetime(2025, 10, 24, 11, 0),
            conflicting_start=datetime(2025, 10, 24, 10, 30),
            conflicting_end=datetime(2025, 10, 24, 11, 30),
        )

        assert conflict.triggered_event_id == 1
        assert conflict.triggered_event_type == "task"
        assert conflict.conflicting_event_id == 2
        assert conflict.conflicting_event_type == "habit_instance"
        assert conflict.conflict_type == ConflictType.OVERLAP
        assert conflict.triggered_start == datetime(2025, 10, 24, 10, 0)
        assert conflict.triggered_end == datetime(2025, 10, 24, 11, 0)
        assert conflict.conflicting_start == datetime(2025, 10, 24, 10, 30)
        assert conflict.conflicting_end == datetime(2025, 10, 24, 11, 30)

    def test_br_event_002_conflict_type_overlap(self):
        """BR-EVENT-002: ConflictType OVERLAP identifica sobreposição."""
        conflict = Conflict(
            triggered_event_id=1,
            triggered_event_type="task",
            conflicting_event_id=2,
            conflicting_event_type="task",
            conflict_type=ConflictType.OVERLAP,
            triggered_start=datetime(2025, 10, 24, 10, 0),
            triggered_end=datetime(2025, 10, 24, 11, 0),
            conflicting_start=datetime(2025, 10, 24, 10, 30),
            conflicting_end=datetime(2025, 10, 24, 11, 30),
        )

        assert conflict.conflict_type == ConflictType.OVERLAP
        assert conflict.conflict_type.value == "overlap"

    def test_br_event_002_conflict_type_sequential(self):
        """BR-EVENT-002: ConflictType SEQUENTIAL identifica eventos consecutivos."""
        conflict = Conflict(
            triggered_event_id=1,
            triggered_event_type="task",
            conflicting_event_id=2,
            conflicting_event_type="task",
            conflict_type=ConflictType.SEQUENTIAL,
            triggered_start=datetime(2025, 10, 24, 10, 0),
            triggered_end=datetime(2025, 10, 24, 11, 0),
            conflicting_start=datetime(2025, 10, 24, 11, 0),
            conflicting_end=datetime(2025, 10, 24, 12, 0),
        )

        assert conflict.conflict_type == ConflictType.SEQUENTIAL
        assert conflict.conflict_type.value == "sequential"

    def test_br_event_002_conflict_suporta_diferentes_tipos_eventos(self):
        """BR-EVENT-002: Conflict suporta task, habit_instance, event."""
        tipos_validos = ["task", "habit_instance", "event"]

        for tipo1 in tipos_validos:
            for tipo2 in tipos_validos:
                conflict = Conflict(
                    triggered_event_id=1,
                    triggered_event_type=tipo1,
                    conflicting_event_id=2,
                    conflicting_event_type=tipo2,
                    conflict_type=ConflictType.OVERLAP,
                    triggered_start=datetime(2025, 10, 24, 10, 0),
                    triggered_end=datetime(2025, 10, 24, 11, 0),
                    conflicting_start=datetime(2025, 10, 24, 10, 30),
                    conflicting_end=datetime(2025, 10, 24, 11, 30),
                )

                assert conflict.triggered_event_type == tipo1
                assert conflict.conflicting_event_type == tipo2


class TestConflictTypeEnum:
    """Testes para ConflictType enum."""

    def test_conflict_type_valores_validos(self):
        """ConflictType possui valores corretos."""
        assert ConflictType.OVERLAP.value == "overlap"
        assert ConflictType.SEQUENTIAL.value == "sequential"

    def test_conflict_type_comparacao(self):
        """ConflictType pode ser comparado."""
        assert ConflictType.OVERLAP == ConflictType.OVERLAP
        assert ConflictType.SEQUENTIAL == ConflictType.SEQUENTIAL
        assert ConflictType.OVERLAP != ConflictType.SEQUENTIAL
