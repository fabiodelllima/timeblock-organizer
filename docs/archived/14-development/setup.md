# Development Setup

## Requisitos

- Python 3.11+
- SQLite 3.35+

## Instalação

```shell
git clone https://github.com/fabiodelllima/timeblock-organizer
cd timeblock-organizer/cli
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## Testes

```shell
pytest
pytest --cov
```
