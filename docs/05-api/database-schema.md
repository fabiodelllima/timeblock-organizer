# Schema do Banco de Dados

**Versão:** 1.0.0  
**Data:** 31 de Outubro de 2025  
**Engine:** SQLite 3.x  
**ORM:** SQLModel

## Tabelas Principais

### routine
```sql
CREATE TABLE routine (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME
);
```

### habit
```sql
CREATE TABLE habit (
    id INTEGER PRIMARY KEY,
    routine_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    scheduled_start TIME NOT NULL,
    scheduled_end TIME NOT NULL,
    recurrence VARCHAR(20) NOT NULL,
    FOREIGN KEY (routine_id) REFERENCES routine(id) ON DELETE CASCADE
);
```

### habit_instance
```sql
CREATE TABLE habit_instance (
    id INTEGER PRIMARY KEY,
    habit_id INTEGER NOT NULL,
    date DATE NOT NULL,
    scheduled_start TIME NOT NULL,
    scheduled_end TIME NOT NULL,
    actual_start DATETIME,
    actual_end DATETIME,
    status VARCHAR(20) DEFAULT 'PLANNED',
    user_override BOOLEAN DEFAULT 0,
    FOREIGN KEY (habit_id) REFERENCES habit(id) ON DELETE CASCADE,
    UNIQUE(habit_id, date)
);
```

### task
```sql
CREATE TABLE task (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    scheduled_date DATE NOT NULL,
    scheduled_start TIME NOT NULL,
    scheduled_end TIME NOT NULL,
    priority INTEGER DEFAULT 3,
    completed BOOLEAN DEFAULT 0
);
```

### time_log
```sql
CREATE TABLE time_log (
    id INTEGER PRIMARY KEY,
    habit_instance_id INTEGER,
    started_at DATETIME NOT NULL,
    ended_at DATETIME NOT NULL,
    duration_minutes INTEGER NOT NULL,
    FOREIGN KEY (habit_instance_id) REFERENCES habit_instance(id)
);
```

## Índices
```sql
CREATE INDEX idx_habit_instance_date ON habit_instance(date);
CREATE INDEX idx_task_date ON task(scheduled_date);
```

## Localização

- Desenvolvimento: `~/.config/timeblock/timeblock.db`
- Testes: `:memory:` (in-memory)
