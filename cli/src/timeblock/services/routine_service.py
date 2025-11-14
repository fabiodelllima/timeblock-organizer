"""Service para gerenciar rotinas."""

from sqlmodel import Session, select

from ..models.routine import Routine


class RoutineService:
    """
    Service para operações de rotinas.

    Responsabilidades:
    - CRUD de rotinas
    - Ativação/desativação de rotinas
    - Busca de rotina ativa
    """

    def __init__(self, session: Session) -> None:
        """Inicializa service com sessão do banco."""
        self.session = session

    def create_routine(self, name: str) -> Routine:
        """
        Cria nova rotina.

        Args:
            name: Nome da rotina

        Returns:
            Rotina criada
        """
        routine = Routine(name=name, is_active=True)
        self.session.add(routine)
        self.session.commit()
        self.session.refresh(routine)
        return routine

    def get_routine(self, routine_id: int) -> Routine | None:
        """
        Busca rotina por ID.

        Args:
            routine_id: ID da rotina

        Returns:
            Rotina encontrada ou None
        """
        return self.session.get(Routine, routine_id)

    def get_active_routine(self) -> Routine | None:
        """
        Busca a rotina ativa atual.

        Retorna a primeira rotina com is_active=True encontrada.
        Se não houver rotina ativa, retorna None.

        Returns:
            Rotina ativa ou None se não houver rotina ativa

        Referências:
            - BR-ROUTINE-001: Uma rotina pode estar ativa
            - BR-HABIT-001: Hábitos são criados na rotina ativa
        """
        statement = select(Routine).where(Routine.is_active)
        result = self.session.exec(statement).first()
        return result

    def list_routines(self, active_only: bool = True) -> list[Routine]:
        """
        Lista rotinas.

        Args:
            active_only: Se True, lista apenas rotinas ativas

        Returns:
            Lista de rotinas
        """
        statement = select(Routine)
        if active_only:
            statement = statement.where(Routine.is_active)

        routines = self.session.exec(statement).all()
        return list(routines)

    def activate_routine(self, routine_id: int) -> None:
        """
        Ativa uma rotina e desativa todas as outras.

        Args:
            routine_id: ID da rotina a ativar
        """
        # Desativar todas
        statement = select(Routine).where(Routine.is_active)
        active_routines = self.session.exec(statement).all()
        for routine in active_routines:
            routine.is_active = False
            self.session.add(routine)

        # Ativar a escolhida
        routine = self.session.get(Routine, routine_id)
        if routine:
            routine.is_active = True
            self.session.add(routine)

        self.session.commit()

    def deactivate_routine(self, routine_id: int) -> None:
        """
        Desativa uma rotina.

        Args:
            routine_id: ID da rotina a desativar
        """
        routine = self.session.get(Routine, routine_id)
        if routine:
            routine.is_active = False
            self.session.add(routine)
            self.session.commit()

    def delete_routine(self, routine_id: int) -> None:
        """
        Deleta uma rotina.

        Args:
            routine_id: ID da rotina a deletar
        """
        routine = self.session.get(Routine, routine_id)
        if routine:
            self.session.delete(routine)
            self.session.commit()
