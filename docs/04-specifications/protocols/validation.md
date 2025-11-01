# Validation Protocol

## RRULE Validation

```python
def validate_rrule(rrule: str) -> bool:
    try:
        dateutil.rrule.rrulestr(rrule)
        return True
    except ValueError:
        return False
```

## Input Validation

- Strings: max_length, non-empty
- Integers: range checks
- Dates: timezone-aware, not past
- Priority: 1-5 range
