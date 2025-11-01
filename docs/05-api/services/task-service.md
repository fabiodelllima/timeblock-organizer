# TaskService

## API

```python
class TaskService:
    def __init__(self, session: Session):
        self.session = session

    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        deadline: Optional[datetime] = None,
        priority: int = 3,
        estimated_duration: Optional[int] = None
    ) -> Task:
        """Cria task com validação."""

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        due_today: bool = False,
        overdue: bool = False
    ) -> List[Task]:
        """Lista tasks com filtros."""

    def complete_task(self, task_id: int) -> Task:
        """Marca como completa."""

    def update_priority(self, task_id: int, new_priority: int) -> Task:
        """Atualiza prioridade."""

    def reschedule(self, task_id: int, new_deadline: datetime) -> Task:
        """Move deadline."""
```

## Exemplo

```python
service = TaskService(session)

# Criar
task = service.create_task(
    "Finalizar relatório",
    deadline=datetime(2025, 11, 1),
    priority=4,
    estimated_duration=120
)

# Listar overdue
overdue = service.list_tasks(overdue=True)

# Completar
service.complete_task(task.id)
```

## Estados

- PENDING: Criada, não iniciada
- IN_PROGRESS: Em execução
- COMPLETED: Finalizada
- CANCELLED: Cancelada
