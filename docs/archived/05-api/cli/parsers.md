# CLI Parsers

## Date Parser

```python
def parse_date(date_str: str) -> datetime:
    """
    Suporta:
    - ISO: 2025-11-01
    - Relativo: today, tomorrow, +3d
    - Natural: next monday
    """
```

## RRULE Parser

```python
def parse_rrule(rrule_str: str) -> rrule:
    """Valida e converte RRULE string."""
```
