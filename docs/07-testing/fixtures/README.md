# Test Fixtures

## Database Fixtures

```python
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```

## Model Fixtures

```python
@pytest.fixture
def habit():
    return Habit(
        name="Test Habit",
        recurrence_rule="FREQ=DAILY",
        default_duration=15,
        priority=3
    )
```
