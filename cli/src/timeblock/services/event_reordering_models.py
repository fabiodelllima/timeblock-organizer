"""Modelos para sistema de reordenamento de eventos."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ConflictType(str, Enum):
    """Tipos de conflitos entre eventos."""

    OVERLAP = "overlap"  # Intervalos de tempo se sobrepõem
    SEQUENTIAL = "sequential"  # Eventos são consecutivos


@dataclass
class Conflict:
    """Representa um conflito entre dois eventos."""

    triggered_event_id: int
    triggered_event_type: str  # "task", "habit_instance", "event"
    conflicting_event_id: int
    conflicting_event_type: str
    conflict_type: ConflictType
    triggered_start: datetime
    triggered_end: datetime
    conflicting_start: datetime
    conflicting_end: datetime
