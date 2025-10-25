"""Models for event reordering system."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EventPriority(int, Enum):
    """Priority levels for event reordering."""

    CRITICAL = 1  # Task deadline < 24h or event IN_PROGRESS
    HIGH = 2  # Event PAUSED
    NORMAL = 3  # Event PLANNED with start < 1h
    LOW = 4  # Event PLANNED with start > 1h


class ConflictType(str, Enum):
    """Types of conflicts between events."""

    OVERLAP = "overlap"  # Time ranges overlap
    SEQUENTIAL = "sequential"  # Events are back-to-back


@dataclass
class Conflict:
    """Represents a conflict between two events."""

    triggered_event_id: int
    triggered_event_type: str  # "task", "habit_instance", "event"
    conflicting_event_id: int
    conflicting_event_type: str
    conflict_type: ConflictType
    triggered_start: datetime
    triggered_end: datetime
    conflicting_start: datetime
    conflicting_end: datetime


@dataclass
class ProposedChange:
    """Represents a proposed change to an event's schedule."""

    event_id: int
    event_type: str
    event_title: str
    current_start: datetime
    current_end: datetime
    proposed_start: datetime
    proposed_end: datetime
    priority: EventPriority
    reason: str  # Human-readable explanation


@dataclass
class ReorderingProposal:
    """Complete proposal for reordering conflicting events."""

    conflicts: list[Conflict]
    proposed_changes: list[ProposedChange]
    estimated_duration_shift: int  # Total minutes shifted

    def has_changes(self) -> bool:
        """Check if proposal contains any changes."""
        return len(self.proposed_changes) > 0

    def get_affected_event_ids(self) -> set[tuple[int, str]]:
        """Get all affected event IDs as (id, type) tuples."""
        affected = set()
        for change in self.proposed_changes:
            affected.add((change.event_id, change.event_type))
        return affected
