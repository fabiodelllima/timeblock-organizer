"""HabitInstance model - Refatorado com Status+Substatus (BR-HABIT-INSTANCE-STATUS-001)."""
from datetime import date as date_type
from datetime import datetime, time
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from .enums import DoneSubstatus, NotDoneSubstatus, SkipReason, Status

if TYPE_CHECKING:
    from .habit import Habit


class HabitInstance(SQLModel, table=True):
    """Instância específica de hábito em data específica.

    Implementa BR-HABIT-INSTANCE-STATUS-001:
    - Status principal: PENDING/DONE/NOT_DONE
    - Substatus detalhado para completion e skip
    - Validações de consistência entre campos
    """

    __tablename__ = "habitinstance"

    id: int | None = Field(default=None, primary_key=True)
    habit_id: int = Field(foreign_key="habits.id")
    date: date_type = Field(index=True)
    scheduled_start: time
    scheduled_end: time
    status: Status = Field(default=Status.PENDING)
    done_substatus: DoneSubstatus | None = Field(default=None)
    not_done_substatus: NotDoneSubstatus | None = Field(default=None)
    skip_reason: SkipReason | None = Field(default=None)
    skip_note: str | None = Field(default=None)
    completion_percentage: int | None = Field(default=None)
    habit: Optional["Habit"] = Relationship(back_populates="instances")

    @property
    def is_overdue(self) -> bool:
        """Verifica se instância está atrasada.

        Retorna True apenas se:
        - Status é PENDING
        - Horário atual passou do scheduled_start

        Returns:
            bool: True se atrasado, False caso contrário
        """
        if self.status != Status.PENDING:
            return False
        now = datetime.now()
        scheduled = datetime.combine(self.date, self.scheduled_start)
        return now > scheduled

    def validate_status_consistency(self) -> None:
        """Valida consistência entre status e substatus.

        Regras (BR-HABIT-INSTANCE-STATUS-001):
        1. DONE requer done_substatus preenchido
        2. NOT_DONE requer not_done_substatus preenchido
        3. PENDING não pode ter substatus
        4. Substatus são mutuamente exclusivos
        5. SKIPPED_JUSTIFIED requer skip_reason
        6. skip_reason só permitido com SKIPPED_JUSTIFIED

        Raises:
            ValueError: Se validação falhar
        """
        # Validação para status DONE
        if self.status == Status.DONE:
            if self.done_substatus is None:
                raise ValueError("done_substatus obrigatório quando status=DONE")
            if self.not_done_substatus is not None:
                raise ValueError("not_done_substatus deve ser None quando status=DONE")

        # Validação para status NOT_DONE
        elif self.status == Status.NOT_DONE:
            if self.not_done_substatus is None:
                raise ValueError("not_done_substatus obrigatório quando status=NOT_DONE")
            if self.done_substatus is not None:
                raise ValueError("done_substatus deve ser None quando status=NOT_DONE")

        # Validação para status PENDING
        elif self.status == Status.PENDING:
            if self.done_substatus is not None or self.not_done_substatus is not None:
                raise ValueError("Substatus deve ser None quando status=PENDING")

        # Validação de skip_reason
        if self.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED:
            if self.skip_reason is None:
                raise ValueError("skip_reason obrigatório para SKIPPED_JUSTIFIED")
        else:
            if self.skip_reason is not None:
                raise ValueError("skip_reason só permitido com SKIPPED_JUSTIFIED")
