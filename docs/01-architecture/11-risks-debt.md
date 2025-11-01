# 11. Riscos e Débito Técnico

## Riscos

**Alto:**

- Perda de dados por corrupção SQLite

**Médio:**

- Cascata infinita de conflitos

**Baixo:**

- Performance em 1000+ eventos/dia

## Débito Técnico

- Tuple returns deprecated (migrar)
- Testes E2E ausentes
- TUI não implementado
