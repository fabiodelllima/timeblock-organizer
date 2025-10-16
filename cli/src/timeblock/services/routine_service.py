"""Service para gerenciar rotinas."""

from datetime import datetime

from sqlmodel import Session, select

from src.timeblock.models import Routine


class RoutineService:
    """Gerencia operações CRUD de rotinas."""

    def __init__(self, session: Session) -> None:
        """Inicializa o service com uma sessão de database.

        Args:
            session: Sessão SQLModel para operações de database
        """
        self.session = session

    def create_routine(self, name: str) -> Routine:
        """Cria uma nova rotina.

        Args:
            name: Nome da rotina

        Returns:
            Routine criada

        Raises:
            ValueError: Se o nome for vazio ou maior que 200 caracteres
        """
        if not name or not name.strip():
            raise ValueError("Nome da rotina não pode ser vazio")

        if len(name) > 200:
            raise ValueError("Nome da rotina não pode ter mais de 200 caracteres")

        routine = Routine(
            name=name.strip(),
            is_active=True,
            created_at=datetime.now(),
        )

        self.session.add(routine)
        self.session.commit()
        self.session.refresh(routine)

        return routine

    def get_routine(self, routine_id: int) -> Routine | None:
        """Busca uma rotina por ID.

        Args:
            routine_id: ID da rotina

        Returns:
            Routine encontrada ou None
        """
        return self.session.get(Routine, routine_id)

    def list_routines(self, active_only: bool = True) -> list[Routine]:
        """Lista rotinas.

        Args:
            active_only: Se True, retorna apenas rotinas ativas

        Returns:
            Lista de rotinas
        """
        statement = select(Routine)

        if active_only:
            statement = statement.where(Routine.is_active == True)  # noqa: E712

        statement = statement.order_by(Routine.created_at.desc())

        results = self.session.exec(statement)
        return list(results.all())

    def activate_routine(self, routine_id: int) -> None:
        """Ativa uma rotina.

        Args:
            routine_id: ID da rotina

        Raises:
            ValueError: Se a rotina não existir
        """
        routine = self.get_routine(routine_id)

        if routine is None:
            raise ValueError(f"Rotina com ID {routine_id} não encontrada")

        routine.is_active = True
        self.session.add(routine)
        self.session.commit()

    def deactivate_routine(self, routine_id: int) -> None:
        """Desativa uma rotina.

        Args:
            routine_id: ID da rotina

        Raises:
            ValueError: Se a rotina não existir
        """
        routine = self.get_routine(routine_id)

        if routine is None:
            raise ValueError(f"Rotina com ID {routine_id} não encontrada")

        routine.is_active = False
        self.session.add(routine)
        self.session.commit()

    def delete_routine(self, routine_id: int) -> None:
        """Remove uma rotina do database.

        Args:
            routine_id: ID da rotina

        Raises:
            ValueError: Se a rotina não existir
        """
        routine = self.get_routine(routine_id)

        if routine is None:
            raise ValueError(f"Rotina com ID {routine_id} não encontrada")

        self.session.delete(routine)
        self.session.commit()
