# Fixtures: Time

**Versão:** 1.0.0  
**Data:** 31 de Outubro de 2025

---

## Freezegun Fixtures
```python
import pytest
from freezegun import freeze_time

@pytest.fixture
def frozen_time():
    """Congela tempo em 2025-11-01 08:00:00."""
    with freeze_time("2025-11-01 08:00:00"):
        yield

@pytest.fixture
def monday_morning():
    """Segunda-feira 03/11/2025 às 07:00."""
    with freeze_time("2025-11-03 07:00:00"):
        yield

@pytest.fixture
def friday_evening():
    """Sexta-feira 07/11/2025 às 18:00."""
    with freeze_time("2025-11-07 18:00:00"):
        yield
```

## Time Helpers
```python
@pytest.fixture
def time_utils():
    """Helpers para manipulação de tempo."""
    class TimeUtils:
        @staticmethod
        def today() -> date:
            return date.today()
        
        @staticmethod
        def now() -> datetime:
            return datetime.now()
        
        @staticmethod
        def parse_time(time_str: str) -> time:
            return datetime.strptime(time_str, "%H:%M").time()
        
        @staticmethod
        def add_minutes(t: time, minutes: int) -> time:
            dt = datetime.combine(date.min, t)
            dt += timedelta(minutes=minutes)
            return dt.time()
    
    return TimeUtils()
```

## Uso
```python
def test_with_frozen_time(frozen_time, session):
    """Teste com tempo congelado."""
    instance = create_instance(date=date.today())
    assert instance.date == date(2025, 11, 1)

def test_monday_specific(monday_morning, habit_factory):
    """Teste específico para segunda."""
    habit = habit_factory(recurrence=RecurrenceType.MONDAY)
    assert habit.should_generate(date.today())
```

---

**Localização:** `docs/07-testing/fixtures/time.md`
