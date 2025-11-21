"""Service para gerenciamento de rotinas."""

from sqlmodel import Session, select

from src.timeblock.models import Routine


class RoutineService:
    """Serviço de gerenciamento de rotinas."""

    def __init__(self, session: Session) -> None:
        """Inicializa service com session."""
        self.session = session

    def create_routine(self, name: str, auto_activate: bool = False) -> Routine:
        """
        Cria nova rotina.

        Args:
            name: Nome da rotina
            auto_activate: Se True, ativa automaticamente (apenas se for primeira)

        Returns:
            Routine criada

        Business Rules:
            - BR-ROUTINE-001: Nova routine criada inativa por padrão
            - BR-ROUTINE-004: Primeira routine ativada automaticamente
        """
        name = name.strip()
        if not name:
            raise ValueError("Nome da rotina não pode ser vazio")

        # Verificar se é primeira rotina
        existing = self.session.exec(select(Routine)).first()
        is_first = existing is None

        routine = Routine(name=name, is_active=False)
        self.session.add(routine)
        self.session.flush()  # Gera ID

        # BR-ROUTINE-004: Primeira routine ativada automaticamente
        if is_first or auto_activate:
            self._activate_routine_internal(routine)

        return routine

    def get_routine(self, routine_id: int) -> Routine | None:
        """Busca rotina por ID."""
        return self.session.get(Routine, routine_id)

    def get_active_routine(self) -> Routine | None:
        """
        Retorna routine ativa.

        Business Rules:
            - BR-ROUTINE-004: get_active retorna routine ativa
        """
        return self.session.exec(select(Routine).where(Routine.is_active == True)).first()  # noqa: E712

    def list_routines(self, active_only: bool = False) -> list[Routine]:
        """Lista rotinas."""
        statement = select(Routine)
        if active_only:
            statement = statement.where(Routine.is_active == True)  # noqa: E712
        return list(self.session.exec(statement).all())

    def activate_routine(self, routine_id: int) -> Routine:
        """
        Ativa rotina e desativa outras.

        Business Rules:
            - BR-ROUTINE-001: Apenas uma routine ativa por vez
        """
        routine = self.session.get(Routine, routine_id)
        if routine is None:
            raise ValueError(f"Rotina {routine_id} não encontrada")

        self._activate_routine_internal(routine)
        return routine

    def _activate_routine_internal(self, routine: Routine) -> None:
        """
        Ativa routine e desativa outras (método interno).

        Business Rules:
            - BR-ROUTINE-001: Ativação desativa outras automaticamente
        """
        # Desativar todas
        for other in self.session.exec(select(Routine).where(Routine.is_active == True)).all():  # noqa: E712
            other.is_active = False
            self.session.add(other)

        # Ativar esta
        routine.is_active = True
        self.session.add(routine)

    def deactivate_routine(self, routine_id: int) -> None:
        """Desativa rotina."""
        routine = self.session.get(Routine, routine_id)
        if routine is None:
            raise ValueError(f"Rotina {routine_id} não encontrada")

        routine.is_active = False
        self.session.add(routine)

    def delete_routine(self, routine_id: int) -> None:
        """
        Soft delete de rotina (marca deleted_at).

        MVP: Soft delete simples.
        Fase 2: Implementar soft delete em cascata.

        Business Rules:
            - BR-ROUTINE-002: Soft delete como padrão (preserva histórico)
        """
        routine = self.session.get(Routine, routine_id)
        if routine is None:
            raise ValueError(f"Rotina {routine_id} não encontrada")

        # TODO Fase 2: Implementar soft delete
        # Por ora, fazer hard delete simples
        self.session.delete(routine)

    def hard_delete_routine(self, routine_id: int, force: bool = False) -> None:
        """
        Deleta rotina PERMANENTEMENTE (HARD DELETE).

        FK RESTRICT bloqueia delete se tiver habits.
        Fase 2: force=True permite cascade delete.

        Args:
            routine_id: ID da rotina a deletar
            force: Se True, permite cascade delete (Fase 2)

        Raises:
            IntegrityError: Se rotina tem habits (FK RESTRICT do banco)
            ValueError: Se rotina não existe

        Business Rules:
            - BR-ROUTINE-002: Hard delete bloqueia se tiver habits (FK RESTRICT)
            - BR-HABIT-003: Delete routine com habits bloqueado pelo banco
        """
        routine = self.session.get(Routine, routine_id)
        if routine is None:
            raise ValueError(f"Rotina {routine_id} não encontrada")

        # TODO Fase 2: Implementar cascade delete quando force=True
        # Deixar FK RESTRICT do banco bloquear delete se tiver habits
        self.session.delete(routine)
        self.session.commit()

    def update_routine(self, routine_id: int, name: str | None = None) -> Routine | None:
        """Atualiza nome da rotina."""
        routine = self.session.get(Routine, routine_id)
        if routine is None:
            return None

        if name is not None:
            name = name.strip()
            if not name:
                raise ValueError("Nome da rotina não pode ser vazio")
            routine.name = name
            self.session.add(routine)

        return routine
