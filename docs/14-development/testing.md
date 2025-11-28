# Testing Guide

## Estrutura

```terminal
tests/
├── unit/
├── integration/
└── conftest.py
```

## Fixtures

```python
@pytest.fixture
def habit():
    return Habit(name="Test", recurrence_rule="FREQ=DAILY", default_duration=15)
```

## Coverage

Target: > 90%
