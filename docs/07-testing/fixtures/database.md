# Fixtures: Database

**Versão:** 1.0.0  
**Data:** 31 de Outubro de 2025

---

## Database Session Fixture
```python
@pytest.fixture
def session():
    """In-memory SQLite session para testes."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
        session.rollback()
```

## Factory Fixtures
```python
@pytest.fixture
def routine_factory(session):
    """Factory para criar rotinas."""
    def _create(name="Test Routine", is_active=True):
        routine = Routine(name=name, is_active=is_active)
        session.add(routine)
        session.commit()
        session.refresh(routine)
        return routine
    return _create

@pytest.fixture
def habit_factory(session, routine_factory):
    """Factory para criar hábitos."""
    def _create(
        routine=None,
        title="Test Habit",
        start=time(7, 0),
        end=time(8, 0),
        recurrence=RecurrenceType.DAILY
    ):
        if routine is None:
            routine = routine_factory()
        
        habit = Habit(
            routine_id=routine.id,
            title=title,
            scheduled_start=start,
            scheduled_end=end,
            recurrence=recurrence
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)
        return habit
    return _create

@pytest.fixture
def instance_factory(session, habit_factory):
    """Factory para criar instâncias."""
    def _create(
        habit=None,
        date_=None,
        status=HabitInstanceStatus.PLANNED
    ):
        if habit is None:
            habit = habit_factory()
        if date_ is None:
            date_ = date.today()
        
        instance = HabitInstance(
            habit_id=habit.id,
            date=date_,
            scheduled_start=habit.scheduled_start,
            scheduled_end=habit.scheduled_end,
            status=status
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)
        return instance
    return _create
```

## Dados Pré-Populados
```python
@pytest.fixture
def populated_db(session, routine_factory, habit_factory):
    """Database com dados realistas."""
    morning = routine_factory(name="Morning Routine")
    evening = routine_factory(name="Evening Routine")
    
    # Morning habits
    meditation = habit_factory(
        routine=morning,
        title="Meditation",
        start=time(6, 0),
        end=time(6, 20),
        recurrence=RecurrenceType.DAILY
    )
    
    exercise = habit_factory(
        routine=morning,
        title="Exercise",
        start=time(7, 0),
        end=time(8, 0),
        recurrence=RecurrenceType.MONDAY
    )
    
    # Evening habits
    reading = habit_factory(
        routine=evening,
        title="Reading",
        start=time(21, 0),
        end=time(22, 0),
        recurrence=RecurrenceType.DAILY
    )
    
    return {
        "routines": [morning, evening],
        "habits": [meditation, exercise, reading]
    }
```

---

**Localização:** `docs/07-testing/fixtures/database.md`
