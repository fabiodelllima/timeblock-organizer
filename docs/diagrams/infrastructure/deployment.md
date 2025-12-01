# Diagrama de Deployment

- **Versão:** 1.0.0
- **Data:** 31 de Outubro de 2025

```mermaid
graph TB
    subgraph UserMachine["Máquina do Usuário"]
        CLI[TimeBlock CLI<br/>Python 3.12+]
        DB[(SQLite<br/>~/.config/timeblock/timeblock.db)]
    end

    CLI -->|Read/Write| DB
```

**Componentes:**

- CLI: Python 3.12+, Typer
- DB: SQLite 3.x, local
- Dependências: typer, sqlmodel, rich, pydantic
