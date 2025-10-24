"""Tests for event reordering models."""
from datetime import datetime
import pytest
from src.timeblock.services.event_reordering_models import (
    EventPriority,
    ConflictType,
    Conflict,
    ProposedChange,
    ReorderingProposal,
)


class TestEventPriority:
    """Tests for EventPriority enum."""

    def test_priority_values(self):
        """Priority values are in correct order."""
        assert EventPriority.CRITICAL == 1
        assert EventPriority.HIGH == 2
        assert EventPriority.NORMAL == 3
        assert EventPriority.LOW == 4

    def test_priority_comparison(self):
        """Priorities can be compared."""
        assert EventPriority.CRITICAL < EventPriority.HIGH
        assert EventPriority.HIGH < EventPriority.NORMAL
        assert EventPriority.NORMAL < EventPriority.LOW


class TestConflictType:
    """Tests for ConflictType enum."""

    def test_conflict_types(self):
        """Conflict types have correct values."""
        assert ConflictType.OVERLAP == "overlap"
        assert ConflictType.SEQUENTIAL == "sequential"


class TestConflict:
    """Tests for Conflict dataclass."""

    def test_create_conflict(self):
        """Can create conflict instance."""
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
        assert conflict.conflict_type == ConflictType.OVERLAP


class TestProposedChange:
    """Tests for ProposedChange dataclass."""

    def test_create_proposed_change(self):
        """Can create proposed change instance."""
        change = ProposedChange(
            event_id=1,
            event_type="task",
            event_title="Task 1",
            current_start=datetime(2025, 10, 24, 10, 0),
            current_end=datetime(2025, 10, 24, 11, 0),
            proposed_start=datetime(2025, 10, 24, 11, 0),
            proposed_end=datetime(2025, 10, 24, 12, 0),
            priority=EventPriority.LOW,
            reason="Moved to resolve conflict",
        )
        assert change.event_id == 1
        assert change.priority == EventPriority.LOW


class TestReorderingProposal:
    """Tests for ReorderingProposal dataclass."""

    def test_create_empty_proposal(self):
        """Can create empty proposal."""
        proposal = ReorderingProposal(
            conflicts=[],
            proposed_changes=[],
            estimated_duration_shift=0,
        )
        assert not proposal.has_changes()
        assert len(proposal.get_affected_event_ids()) == 0

    def test_has_changes(self):
        """has_changes() returns correct value."""
        change = ProposedChange(
            event_id=1,
            event_type="task",
            event_title="Task 1",
            current_start=datetime(2025, 10, 24, 10, 0),
            current_end=datetime(2025, 10, 24, 11, 0),
            proposed_start=datetime(2025, 10, 24, 11, 0),
            proposed_end=datetime(2025, 10, 24, 12, 0),
            priority=EventPriority.LOW,
            reason="Moved",
        )
        proposal = ReorderingProposal(
            conflicts=[],
            proposed_changes=[change],
            estimated_duration_shift=60,
        )
        assert proposal.has_changes()

    def test_get_affected_event_ids(self):
        """get_affected_event_ids() returns all affected events."""
        changes = [
            ProposedChange(
                event_id=1,
                event_type="task",
                event_title="Task 1",
                current_start=datetime(2025, 10, 24, 10, 0),
                current_end=datetime(2025, 10, 24, 11, 0),
                proposed_start=datetime(2025, 10, 24, 11, 0),
                proposed_end=datetime(2025, 10, 24, 12, 0),
                priority=EventPriority.LOW,
                reason="Moved",
            ),
            ProposedChange(
                event_id=2,
                event_type="habit_instance",
                event_title="Habit 1",
                current_start=datetime(2025, 10, 24, 11, 0),
                current_end=datetime(2025, 10, 24, 12, 0),
                proposed_start=datetime(2025, 10, 24, 12, 0),
                proposed_end=datetime(2025, 10, 24, 13, 0),
                priority=EventPriority.NORMAL,
                reason="Shifted",
            ),
        ]
        proposal = ReorderingProposal(
            conflicts=[],
            proposed_changes=changes,
            estimated_duration_shift=120,
        )
        affected = proposal.get_affected_event_ids()
        assert len(affected) == 2
        assert (1, "task") in affected
        assert (2, "habit_instance") in affected
