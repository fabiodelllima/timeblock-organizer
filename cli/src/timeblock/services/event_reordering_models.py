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


@dataclass
class ProposedChange:
    """Representa uma mudança proposta para resolver conflito."""

    event_id: int
    event_type: str  # "task", "habit_instance", "event"
    original_start: datetime
    original_end: datetime
    proposed_start: datetime
    proposed_end: datetime
    priority: int  # Usado para ordenação


@dataclass
class ReorderingProposal:
    """Proposta completa de reordenamento para resolver conflitos."""

    conflicts: list[Conflict]
    proposed_changes: list[ProposedChange]
    estimated_duration_shift: int  # minutos totais de atraso
    affected_events_count: int
