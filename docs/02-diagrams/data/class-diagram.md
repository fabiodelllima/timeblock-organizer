# Diagrama de Classes: Models

- **Versão:** 1.0.0
- **Data:** 31 de Outubro de 2025

```mermaid
classDiagram
    class Routine {
        +int id
        +str name
        +bool is_active
    }

    class Habit {
        +int id
        +int routine_id
        +str title
        +time scheduled_start
        +time scheduled_end
        +RecurrenceType recurrence
    }

    class HabitInstance {
        +int id
        +int habit_id
        +date date
        +HabitInstanceStatus status
        +bool user_override
    }

    class Task {
        +int id
        +str title
        +date scheduled_date
        +int priority
        +bool completed
    }

    class TimeLog {
        +int id
        +int habit_instance_id
        +datetime started_at
        +datetime ended_at
    }

    Routine "1" --> "*" Habit : contém
    Habit "1" --> "*" HabitInstance : gera
    HabitInstance "1" --> "*" TimeLog : registra
```

**Relacionamentos:**

- Routine → Habit: 1:N (cascade delete)
- Habit → HabitInstance: 1:N (cascade delete)
- HabitInstance → TimeLog: 1:N
