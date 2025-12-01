# Problemas Arquiteturais Identificados

- **Versão**: 2.0
- **Data**: 21 de Outubro de 2025

---

## 1. Acoplamento Services-Repositories

**Problema**: Services importam diretamente repositories concretos, violando Dependency Inversion Principle.

**Impacto**: Dificulta testes unitários com mocks.

**Solução**: Introduzir Protocol interfaces.

```python
from typing import Protocol

class IRoutineRepository(Protocol):
    def save(self, routine: Routine) -> Routine: ...
    def find_by_id(self, id: int) -> Routine | None: ...

class RoutineService:
    def __init__(self, repository: IRoutineRepository):
        self.repository = repository
```

---

## 2. Gerenciamento de Sessões

**Problema**: Não está claro como sessões SQLModel são gerenciadas. Risco de vazamentos.

**Solução**: Implementar padrão Unit of Work com context managers.

```python
from contextlib import contextmanager

@contextmanager
def get_session():
    engine = get_engine()
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
```

---

## 3. Validação Distribuída

**Problema**: Validação espalhada entre CLI, services e models.

**Solução**: Centralizar validações de domínio nos models com Pydantic validators.

```python
from pydantic import validator

class Habit(SQLModel, table=True):
    scheduled_start: time
    scheduled_end: time

    @validator('scheduled_end')
    def end_after_start(cls, v, values):
        if 'scheduled_start' in values and v <= values['scheduled_start']:
            raise ValueError('end must be after start')
        return v
```

---

## 4. Concorrência

**Problema**: Sem mecanismos para lidar com concorrência. Risco de race conditions.

**Solução**: Implementar locking pessimista.

```python
def activate_routine(self, routine_id: int) -> Routine:
    with get_session() as session:
        session.execute(text("BEGIN IMMEDIATE"))

        current_active = session.exec(
            select(Routine)
            .where(Routine.is_active == True)
            .with_for_update()
        ).first()

        if current_active:
            current_active.is_active = False
            session.add(current_active)

        routine = session.exec(
            select(Routine)
            .where(Routine.id == routine_id)
            .with_for_update()
        ).first()

        routine.is_active = True
        session.commit()
        return routine
```

---

## 5. Geração Não-Incremental

**Problema**: HabitInstanceService gera instâncias para 8 semanas completas toda vez.

**Solução**: Implementar geração incremental.

```python
def generate_instances(self, habit_id: int, horizon_weeks: int = 8):
    with get_session() as session:
        repository = HabitInstanceRepository(session)

        last_instance = repository.find_last_for_habit(habit_id)

        if last_instance:
            start_date = last_instance.date + timedelta(days=1)
        else:
            start_date = date.today()

        end_date = start_date + timedelta(weeks=horizon_weeks)
        return self._generate_for_range(habit_id, start_date, end_date)
```

---

## 6. Timer Sem Persistência

**Problema**: Timer mantém estado em memória sem checkpoints.

**Solução**: Implementar checkpoints periódicos.

```python
import threading

class TimerService:
    def __init__(self, repository):
        self.repository = repository
        self._checkpoint_interval = 30

    def start_timer(self, habit_instance_id: int):
        timer = self._create_timer_log(habit_instance_id)

        def checkpoint():
            while self._timer_running(timer.id):
                time.sleep(self._checkpoint_interval)
                self._update_duration(timer.id)

        thread = threading.Thread(target=checkpoint, daemon=True)
        thread.start()
        return timer
```

---

## 7. Versionamento de Schema

**Problema**: Migrations básico sem rastreamento de versão.

**Solução**: Implementar versionamento com tabela de metadados.

```python
class Migration(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    version: str = Field(unique=True)
    applied_at: datetime
    description: str
```

---

## 8. Relatórios Sem Cache

**Problema**: ReportService executa queries complexas sempre.

**Solução**: Implementar cache com invalidação.

```python
from functools import lru_cache

class ReportService:
    @lru_cache(maxsize=128)
    def _cached_weekly_report(self, start_date, end_date):
        return self._compute_weekly_report(start_date, end_date)
```

---

## 9. Timezone

**Problema**: Usa datetime sem timezone.

**Solução**: Armazenar em UTC, converter na apresentação.

```python
from datetime import timezone

class TimeLog(SQLModel, table=True):
    start_time: datetime

    def __init__(self, **data):
        if 'start_time' in data and data['start_time'].tzinfo is None:
            data['start_time'] = data['start_time'].replace(tzinfo=timezone.utc)
        super().__init__(**data)
```

---

## 10. Observabilidade

**Problema**: Sem sistema estruturado de logging.

**Solução**: Implementar logging estruturado.

```python
import structlog

logger = structlog.get_logger()

class RoutineService:
    def create_routine(self, name: str):
        log = logger.bind(operation="create_routine")
        log.info("creating_routine", routine_name=name)

        try:
            routine = Routine(name=name)
            saved = self.repository.save(routine)
            log.info("routine_created", routine_id=saved.id)
            return saved
        except Exception as e:
            log.error("creation_failed", error=str(e))
            raise
```

---

## Priorização

**Alta Prioridade**:

1. Abstrações de Repository
2. Gerenciamento de Sessões
3. Observabilidade

**Média Prioridade**: 4. Validação Centralizada 5. Timer com Checkpoints 6. Timezone

**Baixa Prioridade**: 7. Cache de Relatórios 8. Geração Incremental 9. Versionamento de Migrations 10. Concorrência

---

- **Versão**: 2.0
- **Próxima revisão**: Trimestral
