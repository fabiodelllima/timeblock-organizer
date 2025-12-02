"""
Integration tests - TaskService + EventReorderingService.

Testa integração entre TaskService e EventReorderingService,
validando atualizações de tasks, detecção de conflitos e propostas.

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
    - Sprint 2.2: Task + EventReordering integration
"""

from datetime import datetime, timedelta

from sqlmodel import Session

from src.timeblock.database import get_engine_context
from src.timeblock.models.habit import Recurrence
from src.timeblock.services.habit_instance_service import HabitInstanceService
from src.timeblock.services.habit_service import HabitService
from src.timeblock.services.routine_service import RoutineService
from src.timeblock.services.task_service import TaskService


class TestBRTaskReordering:
    """
    Integration: TaskService + EventReorderingService (BR-TASK-REORDER-*).

    Valida atualização de tasks com detecção automática de conflitos
    e geração de propostas de reorganização.

    BRs cobertas:
    - BR-TASK-REORDER-001: Atualização sem mudança de horário
    - BR-TASK-REORDER-002: Atualização sem conflitos
    - BR-TASK-REORDER-003: Atualização com conflito de task
    - BR-TASK-REORDER-004: Atualização com conflito de habit
    - BR-TASK-REORDER-005: Atualização de task inexistente
    - BR-TASK-REORDER-006: Atualização para mesmo horário
    """

    def test_br_reorder_001_update_without_time_change(self, test_engine: object) -> None:
        """
        Integration: Atualização sem mudança de horário não dispara reordering.

        DADO: Task existente com horário definido
        QUANDO: Usuário atualiza apenas título/descrição
        ENTÃO: Campos são atualizados
        E: Nenhuma proposta é gerada

        Referências:
            - BR-TASK-REORDER-001: Atualização sem mudança de horário
        """
        # ARRANGE
        now = datetime.now()
        task = TaskService.create_task(title="Review code", scheduled_datetime=now)
        # Type narrowing
        assert task.id is not None
        # ACT
        updated, proposal = TaskService.update_task(
            task.id, title="Review PR", description="Check tests"
        )
        # ASSERT
        assert updated is not None
        assert updated.title == "Review PR"
        assert updated.description == "Check tests"
        assert proposal is None or len(proposal) == 0

    def test_br_reorder_002_update_without_conflicts(self, test_engine: object) -> None:
        """
        Integration: Mudança de horário sem conflitos não gera proposta.

        DADO: Task existente
        QUANDO: Usuário muda horário para slot livre
        ENTÃO: Horário é atualizado
        E: Nenhum conflito é detectado

        Referências:
            - BR-TASK-REORDER-002: Atualização sem conflitos
        """
        # ARRANGE
        now = datetime.now()
        task = TaskService.create_task(title="Review code", scheduled_datetime=now)
        # Type narrowing
        assert task.id is not None
        # ACT
        new_time = now + timedelta(hours=3)
        updated, proposal = TaskService.update_task(task.id, scheduled_datetime=new_time)
        # ASSERT
        assert updated is not None
        assert updated.scheduled_datetime == new_time
        assert proposal is None or len(proposal) == 0

    def test_br_reorder_003_update_with_task_conflict(self, test_engine: object) -> None:
        """
        Integration: Mudança causando conflito com outra task gera proposta.

        DADO: Duas tasks em horários diferentes
        QUANDO: Usuário move task1 para horário de task2
        ENTÃO: Horário é atualizado
        E: Conflito é detectado

        Referências:
            - BR-TASK-REORDER-003: Atualização com conflito de task
        """
        # ARRANGE
        now = datetime.now()
        task1 = TaskService.create_task(title="Task 1", scheduled_datetime=now)
        # Criar task2 para causar conflito potencial
        _task2 = TaskService.create_task(
            title="Task 2", scheduled_datetime=now + timedelta(hours=1)
        )
        # Type narrowing
        assert task1.id is not None
        # ACT
        new_time = now + timedelta(minutes=30)
        updated, conflicts = TaskService.update_task(task1.id, scheduled_datetime=new_time)
        # ASSERT
        assert updated is not None
        assert updated.scheduled_datetime == new_time
        assert conflicts is not None
        assert len(conflicts) > 0, "Deve detectar conflito"

    def test_br_reorder_004_update_conflicts_with_habit(self, test_engine: object) -> None:
        """
        Integration: Task conflitando com HabitInstance gera proposta.

        DADO: HabitInstance em horário definido
        QUANDO: Usuário move task para mesmo horário
        ENTÃO: Conflito é detectado

        Referências:
            - BR-TASK-REORDER-004: Conflito com habit
        """
        # ARRANGE
        now = datetime.now()
        today = now.date()
        with get_engine_context() as engine, Session(engine) as session:
            routine_service = RoutineService(session)
            routine = routine_service.create_routine("Test Routine")
        # Type narrowing
        assert routine.id is not None
        habit = HabitService.create_habit(
            routine_id=routine.id,
            title="Morning Exercise",
            scheduled_start=now.time(),
            scheduled_end=(now + timedelta(hours=1)).time(),
            recurrence=Recurrence.EVERYDAY,
        )
        # Type narrowing
        assert habit.id is not None
        _instances = HabitInstanceService.generate_instances(habit.id, today, today)

        task = TaskService.create_task(
            title="Important Call", scheduled_datetime=now - timedelta(hours=2)
        )
        # Type narrowing
        assert task.id is not None
        # ACT
        updated, conflicts = TaskService.update_task(
            task.id, scheduled_datetime=now + timedelta(minutes=15)
        )
        # ASSERT
        assert updated is not None
        assert updated.scheduled_datetime == now + timedelta(minutes=15)
        assert conflicts is not None
        assert len(conflicts) > 0, "Deve detectar conflito com habit"

    def test_br_reorder_005_update_nonexistent(self, test_engine: object) -> None:
        """
        Integration: Atualização de task inexistente retorna (None, None).

        DADO: ID 99999 que não existe
        QUANDO: Usuário tenta atualizar
        ENTÃO: Retorna (None, None)
        E: Sistema não trava

        Referências:
            - BR-TASK-REORDER-005: Task inexistente
        """
        # ACT
        updated, proposal = TaskService.update_task(99999, title="New title")
        # ASSERT
        assert updated is None
        assert proposal is None

    def test_br_reorder_006_update_same_time(self, test_engine: object) -> None:
        """
        Integration: Atualização para mesmo horário não dispara reordering.

        DADO: Task com horário definido
        QUANDO: Usuário "atualiza" para mesmo horário
        ENTÃO: Horário permanece igual
        E: Nenhuma proposta é gerada

        Referências:
            - BR-TASK-REORDER-006: Mesmo horário
        """
        # ARRANGE
        now = datetime.now()
        task = TaskService.create_task(title="Task", scheduled_datetime=now)
        # Type narrowing
        assert task.id is not None
        # ACT
        updated, proposal = TaskService.update_task(task.id, scheduled_datetime=now)
        # ASSERT
        assert updated is not None
        assert updated.scheduled_datetime == now
        assert proposal is None or len(proposal) == 0
