"""Enumerações compartilhadas entre modelos."""
from enum import Enum


class Status(str, Enum):
    """Status principal (PENDING/DONE/NOT_DONE)."""
    PENDING = "pending"
    DONE = "done"
    NOT_DONE = "not_done"


class DoneSubstatus(str, Enum):
    """Substatus para eventos DONE."""
    FULL = "full"              # 90-110%
    OVERDONE = "overdone"      # 110-150%
    EXCESSIVE = "excessive"    # >150%
    PARTIAL = "partial"        # <90%


class NotDoneSubstatus(str, Enum):
    """Substatus para eventos NOT_DONE."""
    SKIPPED_JUSTIFIED = "skipped_justified"
    SKIPPED_UNJUSTIFIED = "skipped_unjustified"
    IGNORED = "ignored"


class SkipReason(str, Enum):
    """Categorias de justificativa para skip."""
    HEALTH = "saude"
    WORK = "trabalho"
    FAMILY = "familia"
    TRAVEL = "viagem"
    WEATHER = "clima"
    LACK_RESOURCES = "falta_recursos"
    EMERGENCY = "emergencia"
    OTHER = "outro"
